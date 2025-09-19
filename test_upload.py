#!/usr/bin/env python3
"""
测试文件上传图片分析功能
"""
import requests
import os

def test_analyze_upload():
    """测试文件上传分析"""
    url = "http://127.0.0.1:8212/analyze"
    
    # 检查测试图片是否存在
    if not os.path.exists("test_sample.jpg"):
        print("❌ 测试图片不存在，请先运行 create_test_image.py")
        return False
    
    try:
        # 准备文件和表单数据
        with open("test_sample.jpg", "rb") as f:
            files = {"file": ("test_sample.jpg", f, "image/jpeg")}
            data = {
                "prompt": "请详细描述这张图片的内容，包括颜色、形状和文字",
                "model_name": "MiniCPM-V-4_5-int4"
            }
            
            print("正在上传并分析图片...")
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
    success = test_analyze_upload()
    if success:
        print("\n🎉 文件上传图片分析功能测试成功！")
    else:
        print("\n💥 文件上传图片分析功能测试失败！")