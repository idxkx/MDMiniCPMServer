#!/usr/bin/env python3
"""
测试图片分析功能
"""
import requests
import json

# 测试图片URL - 使用一个公开的测试图片
test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

def test_analyze_url():
    """测试URL图片分析"""
    url = "http://127.0.0.1:8209/analyze-url"
    data = {
        "image_url": test_image_url,
        "prompt": "请详细描述这张图片的内容",
        "model_name": "MiniCPM-V-4-int4"
    }
    
    try:
        print(f"正在分析图片: {test_image_url}")
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        print("✅ 分析成功!")
        print(f"模型: {result['model_used']}")
        print(f"提示词: {result['prompt']}")
        print(f"分析结果: {result['result']}")
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_analyze_url()
    if success:
        print("\n🎉 图片分析功能测试成功！")
    else:
        print("\n💥 图片分析功能测试失败！")