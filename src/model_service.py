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
                self.unload_model()
            
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
        if self.current_model is not None:
            del self.current_model
            self.current_model = None
        
        if self.current_tokenizer is not None:
            del self.current_tokenizer
            self.current_tokenizer = None
        
        self.current_model_name = None
        
        # 清理GPU内存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        gc.collect()
        logger.info("Model unloaded")
    
    def analyze_image(self, image: Image.Image, prompt: str = "请详细描述这张图片的内容") -> Optional[str]:
        """分析图片内容"""
        if self.current_model is None or self.current_tokenizer is None:
            logger.error("No model loaded")
            return None
        
        try:
            # 确保图片是RGB格式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 构建消息格式 - 根据MiniCPM-V官方示例
            msgs = [{'role': 'user', 'content': [image, prompt]}]
            
            logger.info("Starting image analysis...")
            
            # 生成回复 - 回退到稳定的greedy decoding但增加最小输出
            res = self.current_model.chat(
                image=None,  # 图片已在消息中
                msgs=msgs,
                tokenizer=self.current_tokenizer,
                sampling=False,  # 使用greedy decoding避免CUDA问题
                max_new_tokens=1024,
                min_new_tokens=10  # 确保最小输出长度
            )
            
            logger.info("Image analysis completed successfully")
            return res
            
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