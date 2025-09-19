#!/usr/bin/env python3
"""
测试MiniCPM-V-4.5模型
"""
import requests
import os

def test_v4_5_model():
    """测试MiniCPM-V-4.5模型分析"""
    url = "http://127.0.0.1:8211/analyze"
    
    # 检查测试图片是否存在
    if not os.path.exists("realistic_test.jpg"):
        print("❌ 测试图片不存在，请先运行 test_real_image.py")
        return False
    
    try:
        with open("realistic_test.jpg", "rb") as f:
            files = {"file": ("realistic_test.jpg", f, "image/jpeg")}
            data = {
                "prompt": "请详细描述这张图片中的所有元素，包括房子、树木、太阳、云朵等，并分析整体的艺术风格",
                "model_name": "MiniCPM-V-4_5-int4"
            }
            
            print("正在使用MiniCPM-V-4.5模型分析图片...")
            response = requests.post(url, files=files, data=data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            print("✅ MiniCPM-V-4.5分析成功!")
            print(f"文件名: {result['filename']}")
            print(f"模型: {result['model_used']}")
            print(f"提示词: {result['prompt']}")
            print(f"分析结果: {result['result']}")
            return True
            
    except Exception as e:
        print(f"❌ MiniCPM-V-4.5分析失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_v4_5_model()
    if success:
        print("\n🎉 MiniCPM-V-4.5模型测试成功！")
    else:
        print("\n💥 MiniCPM-V-4.5模型测试失败！")