import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image
import torch
from transformers import AutoModel, AutoTokenizer
import gc

logger = logging.getLogger(__name__)


class ModelService:
    """MiniCPM-V 模型服务管理类"""
    
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.current_model = None
        self.current_tokenizer = None
        self.current_model_name = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
    
    def get_available_models(self) -> list[str]:
        """获取可用模型列表"""
        models = []
        if self.models_dir.exists() and self.models_dir.is_dir():
            for p in sorted(self.models_dir.iterdir()):
                if p.is_dir() and any(f.name == "config.json" for f in p.iterdir()):
                    models.append(p.name)
        return models
    
    def load_model(self, model_name: str) -> bool:
        """加载指定模型"""
        if self.current_model_name == model_name and self.current_model is not None:
            logger.info(f"Model {model_name} already loaded")
            return True
        
        model_path = self.models_dir / model_name
        if not model_path.exists():
            logger.error(f"Model path does not exist: {model_path}")
            return False
        
        try:
            # 清理之前的模型
            if self.current_model is not None:
                logger.info(f"Unloading current model: {self.current_model_name}")
                self.unload_model()
                # 等待一下确保内存清理完成
                import time
                time.sleep(2)
            
            logger.info(f"Loading model from {model_path}")
            
            # 加载tokenizer
            self.current_tokenizer = AutoTokenizer.from_pretrained(
                str(model_path),
                trust_remote_code=True
            )
            
            # 加载模型
            self.current_model = AutoModel.from_pretrained(
                str(model_path),
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            if self.device == "cpu":
                self.current_model = self.current_model.to(self.device)
            
            self.current_model.eval()
            self.current_model_name = model_name
            
            logger.info(f"Successfully loaded model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            self.unload_model()
            return False
    
    def unload_model(self):
        """卸载当前模型"""
        logger.info("Starting model unload...")
        
        if self.current_model is not None:
            # 将模型移到CPU以释放GPU内存
            try:
                self.current_model = self.current_model.cpu()
            except:
                pass
            del self.current_model
            self.current_model = None
        
        if self.current_tokenizer is not None:
            del self.current_tokenizer
            self.current_tokenizer = None
        
        self.current_model_name = None
        
        # 强制清理GPU内存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()  # 确保所有CUDA操作完成
        
        # 多次垃圾回收确保彻底清理
        for _ in range(3):
            gc.collect()
        
        logger.info("Model unloaded and memory cleared")
    
    def analyze_image(self, image: Image.Image, prompt: str = "请详细描述这张图片的内容") -> Optional[str]:
        """分析图片内容"""
        if self.current_model is None or self.current_tokenizer is None:
            logger.error("No model loaded")
            return None
        
        try:
            # 确保图片是RGB格式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 构建消息格式 - 图片和文本放在同一个content数组中（符合MiniCPM-V规范）
            msgs = [{'role': 'user', 'content': [image, prompt]}]
            
            logger.info("Starting image analysis...")
            logger.info(f"Message format: {[{'role': 'user', 'content': ['<image>', prompt]}]}")
            
            # 生成回复 - 结合官方格式和稳定参数
            res = self.current_model.chat(
                msgs=msgs,
                tokenizer=self.current_tokenizer,
                sampling=False,  # 必须禁用采样避免CUDA错误
                max_new_tokens=1024,
                enable_thinking=False  # 禁用长思维模式
            )
            
            logger.info(f"Raw result type: {type(res)}")
            logger.info(f"Raw result: {res}")
            
            # 确保返回字符串
            if isinstance(res, list):
                result = res[0] if res else ""
            else:
                result = str(res)
            
            # 清理特殊token
            result = result.replace('<CLS>', '').replace('</CLS>', '').strip()
            
            logger.info(f"Final result: {result}")
            logger.info("Image analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze image: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取当前模型信息"""
        return {
            "loaded": self.current_model is not None,
            "model_name": self.current_model_name,
            "device": self.device,
            "available_models": self.get_available_models()
        }