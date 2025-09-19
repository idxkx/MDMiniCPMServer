#!/usr/bin/env python3
"""
诊断模型加载问题
"""
import sys
sys.path.append('src')

from model_service import ModelService
from pathlib import Path
import logging
import torch

# 配置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def diagnose_models():
    """诊断模型"""
    models_dir = Path("./models")
    service = ModelService(models_dir)
    
    print(f"GPU内存使用情况:")
    if torch.cuda.is_available():
        print(f"总内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        print(f"已分配: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
        print(f"已缓存: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
    
    models_to_test = ["MiniCPM-V-4-int4", "MiniCPM-V-4_5-int4"]
    
    for model_name in models_to_test:
        print(f"\n{'='*50}")
        print(f"测试模型: {model_name}")
        print(f"{'='*50}")
        
        # 检查模型路径
        model_path = models_dir / model_name
        print(f"模型路径: {model_path}")
        print(f"路径存在: {model_path.exists()}")
        
        if model_path.exists():
            config_file = model_path / "config.json"
            print(f"配置文件存在: {config_file.exists()}")
            
            # 尝试加载
            try:
                print("开始加载模型...")
                success = service.load_model(model_name)
                print(f"加载结果: {'成功' if success else '失败'}")
                
                if success:
                    print("模型信息:", service.get_model_info())
                    # 卸载模型释放内存
                    service.unload_model()
                    print("模型已卸载")
                    
            except Exception as e:
                print(f"加载异常: {e}")
                import traceback
                traceback.print_exc()
        
        # 显示内存状态
        if torch.cuda.is_available():
            print(f"当前GPU内存:")
            print(f"已分配: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
            print(f"已缓存: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")

if __name__ == "__main__":
    diagnose_models()