#!/usr/bin/env python3
"""
测试模型加载
"""
import sys
sys.path.append('src')

from model_service import ModelService
from pathlib import Path
import logging

# 配置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_model_loading():
    """测试模型加载"""
    models_dir = Path("./models")
    service = ModelService(models_dir)
    
    print("可用模型:", service.get_available_models())
    
    # 测试加载V4.5模型
    print("\n正在测试加载 MiniCPM-V-4_5-int4...")
    try:
        success = service.load_model("MiniCPM-V-4_5-int4")
        if success:
            print("✅ 模型加载成功")
            print("模型信息:", service.get_model_info())
        else:
            print("❌ 模型加载失败")
    except Exception as e:
        print(f"❌ 模型加载异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_loading()