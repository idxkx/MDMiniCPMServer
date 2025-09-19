import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from enum import Enum
from PIL import Image
import io
from model_service import ModelService

# load env first
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_PORT = int(os.getenv("SERVER_PORT", 8207))
APP_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
MODELS_DIR = Path(os.getenv("MODEL_PATH", "./models"))

app = FastAPI(title="MiniCPM-V Server", version="0.1.0")

# 全局模型服务实例
model_service = ModelService(MODELS_DIR)

# 可用模型枚举
class AvailableModels(str, Enum):
    MINICPM_V4_INT4 = "MiniCPM-V-4-int4"  # 注意：此模型可能有兼容性问题，推荐使用4.5版本
    MINICPM_V4_5_INT4 = "MiniCPM-V-4_5-int4"  # 推荐版本

# Pydantic models
class AnalyzeRequest(BaseModel):
    image_url: str = Field(..., description="图片URL地址")
    prompt: str = Field("请详细描述这张图片的内容", description="分析提示词")

class LoadModelRequest(BaseModel):
    model_name: AvailableModels = Field(..., description="要加载的模型名称，可选值: MiniCPM-V-4-int4, MiniCPM-V-4_5-int4")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "MiniCPM-V Server", "version": app.version}

@app.get("/")
def root():
    return {
        "name": "MiniCPM-V Server",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "models": "/models",
        "analyze": "/analyze",
        "analyze_url": "/analyze-url"
    }

@app.get("/models")
def list_models():
    try:
        available_models = model_service.get_available_models()
        model_info = model_service.get_model_info()
        
        models = []
        for model_name in available_models:
            model_path = MODELS_DIR / model_name
            size = None
            try:
                size = sum(f.stat().st_size for f in model_path.glob("**/*") if f.is_file())
            except Exception:
                pass
            
            models.append({
                "name": model_name,
                "path": str(model_path),
                "approx_bytes": size,
                "loaded": model_name == model_info["model_name"]
            })
        
        return {
            "count": len(models),
            "items": models,
            "current_model": model_info["model_name"],
            "device": model_info["device"]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/load-model")
def load_model(request: LoadModelRequest):
    """
    加载指定模型
    
    可用模型:
    - MiniCPM-V-4-int4: 基础版本，较快推理速度
    - MiniCPM-V-4_5-int4: 增强版本，更好的图片理解能力 (推荐)
    """
    try:
        success = model_service.load_model(request.model_name.value)
        if success:
            return {"status": "success", "message": f"Model {request.model_name.value} loaded successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to load model {request.model_name.value}")
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/unload-model")
def unload_model():
    """
    卸载当前模型
    
    释放GPU内存，为加载其他模型做准备。
    """
    try:
        if model_service.current_model is None:
            return {"status": "success", "message": "No model currently loaded"}
        
        current_model_name = model_service.current_model_name
        model_service.unload_model()
        return {"status": "success", "message": f"Model {current_model_name} unloaded successfully"}
    except Exception as e:
        logger.error(f"Error unloading model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_image_upload(
    file: UploadFile = File(..., description="要分析的图片文件"),
    prompt: str = Form("请详细描述这张图片的内容", description="分析提示词")
):
    """
    分析上传的图片文件
    
    使用当前已加载的模型分析图片内容。如需切换模型，请先调用 /load-model 接口。
    """
    try:
        # 检查是否有已加载的模型
        if model_service.current_model is None:
            raise HTTPException(status_code=400, detail="没有已加载的模型，请先调用 /load-model 加载模型")
        
        # 检查文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必须是图片格式")
        
        # 读取图片
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # 分析图片
        result = model_service.analyze_image(image, prompt)
        if result is None:
            raise HTTPException(status_code=500, detail="图片分析失败")
        
        return {
            "status": "success",
            "result": result,
            "model_used": model_service.current_model_name,
            "prompt": prompt,
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-url")
def analyze_image_url(request: AnalyzeRequest):
    """
    分析图片URL
    
    使用当前已加载的模型分析网络图片。如需切换模型，请先调用 /load-model 接口。
    """
    try:
        import requests
        
        # 检查是否有已加载的模型
        if model_service.current_model is None:
            raise HTTPException(status_code=400, detail="没有已加载的模型，请先调用 /load-model 加载模型")
        
        # 下载图片
        response = requests.get(request.image_url, timeout=30)
        response.raise_for_status()
        
        # 检查内容类型
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="URL 必须指向图片文件")
        
        # 打开图片
        image = Image.open(io.BytesIO(response.content)).convert('RGB')
        
        # 分析图片
        result = model_service.analyze_image(image, request.prompt)
        if result is None:
            raise HTTPException(status_code=500, detail="图片分析失败")
        
        return {
            "status": "success",
            "result": result,
            "model_used": model_service.current_model_name,
            "prompt": request.prompt,
            "image_url": request.image_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=False)
