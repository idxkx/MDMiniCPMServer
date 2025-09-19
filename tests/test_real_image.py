#!/usr/bin/env python3
"""
使用真实图片测试分析功能
"""
import requests
from PIL import Image, ImageDraw, ImageFont
import os

def create_realistic_test_image():
    """创建一个更真实的测试图片"""
    # 创建一个 600x400 的图片，模拟一个简单场景
    width, height = 600, 400
    image = Image.new('RGB', (width, height), color='skyblue')
    
    draw = ImageDraw.Draw(image)
    
    # 绘制地面
    draw.rectangle([0, 300, width, height], fill='green')
    
    # 绘制太阳
    draw.ellipse([450, 50, 550, 150], fill='yellow', outline='orange', width=3)
    
    # 绘制房子
    draw.rectangle([100, 200, 250, 300], fill='lightcoral', outline='darkred', width=2)
    
    # 绘制屋顶
    draw.polygon([(80, 200), (175, 150), (270, 200)], fill='brown', outline='black')
    
    # 绘制门
    draw.rectangle([150, 250, 180, 300], fill='brown', outline='black', width=1)
    
    # 绘制窗户
    draw.rectangle([110, 220, 140, 250], fill='lightblue', outline='black', width=1)
    draw.rectangle([210, 220, 240, 250], fill='lightblue', outline='black', width=1)
    
    # 绘制树
    draw.rectangle([320, 250, 340, 300], fill='brown')  # 树干
    draw.ellipse([300, 180, 360, 240], fill='darkgreen')  # 树冠
    
    # 绘制云朵
    draw.ellipse([50, 80, 120, 120], fill='white')
    draw.ellipse([80, 70, 150, 110], fill='white')
    draw.ellipse([110, 85, 180, 125], fill='white')
    
    # 添加文字
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((20, 350), "A beautiful countryside scene", fill='black', font=font)
    draw.text((20, 370), "House, tree, sun and clouds", fill='black', font=font)
    
    # 保存图片
    image_path = "realistic_test.jpg"
    image.save(image_path, "JPEG", quality=95)
    print(f"真实测试图片已创建: {image_path}")
    
    return image_path

def test_realistic_image():
    """测试真实图片分析"""
    url = "http://127.0.0.1:8211/analyze"
    
    # 创建测试图片
    image_path = create_realistic_test_image()
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": (image_path, f, "image/jpeg")}
            data = {
                "prompt": "请详细描述这张图片中的场景，包括建筑、自然元素、颜色和整体氛围",
                "model_name": "MiniCPM-V-4-int4"
            }
            
            print("正在分析真实场景图片...")
            response = requests.post(url, files=files, data=data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            print("✅ 分析成功!")
            print(f"文件名: {result['filename']}")
            print(f"模型: {result['model_used']}")
            print(f"提示词: {result['prompt']}")
            print(f"分析结果: {result['result']}")
            return True
            
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_realistic_image()
    if success:
        print("\n🎉 真实图片分析功能测试成功！")
    else:
        print("\n💥 真实图片分析功能测试失败！")