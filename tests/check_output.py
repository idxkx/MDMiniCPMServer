#!/usr/bin/env python3
"""
检查模型输出结果
"""
import sys
sys.path.append('src')

from model_service import ModelService
from pathlib import Path
from PIL import Image
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def check_model_output():
    """检查模型实际输出"""
    models_dir = Path("./models")
    service = ModelService(models_dir)
    
    # 加载模型
    print("正在加载模型 MiniCPM-V-4_5-int4...")
    success = service.load_model("MiniCPM-V-4_5-int4")
    
    if not success:
        print("❌ 模型加载失败")
        return
    
    print("✅ 模型加载成功")
    
    # 测试图片分析
    image = Image.open("test_sample.jpg").convert('RGB')
    print("正在分析图片...")
    
    result = service.analyze_image(image, "请详细描述这张图片")
    
    print(f"原始结果: '{result}'")
    print(f"结果类型: {type(result)}")
    print(f"结果长度: {len(result) if result else 0}")
    print(f"结果编码: {result.encode('utf-8') if result else 'None'}")
    
    # 检查是否包含特殊token
    special_tokens = ['<CLS>', '<SEP>', '<PAD>', '<UNK>', '<BOS>', '<EOS>']
    for token in special_tokens:
        if result and token in result:
            print(f"⚠️  发现特殊token: {token}")

if __name__ == "__main__":
    check_model_output()