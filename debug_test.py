#!/usr/bin/env python3
"""
调试测试模型加载和推理
"""
import sys
sys.path.append('src')

from model_service import ModelService
from pathlib import Path
from PIL import Image
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_model_service():
    """直接测试ModelService"""
    models_dir = Path("./models")
    service = ModelService(models_dir)
    
    print("可用模型:", service.get_available_models())
    
    # 加载模型
    print("正在加载模型 MiniCPM-V-4-int4...")
    success = service.load_model("MiniCPM-V-4-int4")
    
    if not success:
        print("❌ 模型加载失败")
        return False
    
    print("✅ 模型加载成功")
    
    # 测试图片分析
    if not Path("test_sample.jpg").exists():
        print("❌ 测试图片不存在")
        return False
    
    image = Image.open("test_sample.jpg").convert('RGB')
    print("正在分析图片...")
    
    result = service.analyze_image(image, "请描述这张图片的内容")
    
    if result:
        print("✅ 图片分析成功")
        print("分析结果:", result)
        return True
    else:
        print("❌ 图片分析失败")
        return False

if __name__ == "__main__":
    success = test_model_service()
    if success:
        print("\n🎉 直接测试成功！")
    else:
        print("\n💥 直接测试失败！")