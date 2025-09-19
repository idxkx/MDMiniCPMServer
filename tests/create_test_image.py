#!/usr/bin/env python3
"""
创建测试图片
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """创建一个简单的测试图片"""
    # 创建一个 400x300 的图片
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='lightblue')
    
    # 获取绘图对象
    draw = ImageDraw.Draw(image)
    
    # 绘制一些简单的图形
    # 绘制矩形
    draw.rectangle([50, 50, 150, 100], fill='red', outline='black', width=2)
    
    # 绘制圆形
    draw.ellipse([200, 50, 300, 150], fill='green', outline='black', width=2)
    
    # 绘制文字
    try:
        # 尝试使用默认字体
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((50, 200), "这是一个测试图片", fill='black', font=font)
    draw.text((50, 220), "Test Image for MiniCPM-V", fill='black', font=font)
    
    # 绘制线条
    draw.line([(50, 250), (350, 250)], fill='purple', width=3)
    
    # 保存图片
    image_path = "test_sample.jpg"
    image.save(image_path, "JPEG")
    print(f"测试图片已创建: {image_path}")
    
    return image_path

if __name__ == "__main__":
    create_test_image()