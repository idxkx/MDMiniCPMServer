#!/usr/bin/env python3
"""
性能测试脚本 - 测试图片分析接口的响应时间

用法：
python tests/benchmark.py --image 1-160Q21I554.jpg --runs 5
"""

import argparse
import json
import time
import statistics
import requests
from pathlib import Path

def benchmark_analyze(server_url: str, image_path: str, prompt: str, runs: int = 5):
    """
    对图片分析接口进行性能测试
    """
    print(f"开始性能测试...")
    print(f"服务器: {server_url}")
    print(f"图片: {image_path}")
    print(f"测试次数: {runs}")
    print(f"提示词: {prompt}")
    print("-" * 50)
    
    response_times = []
    processing_times = []
    
    for i in range(runs):
        print(f"第 {i+1}/{runs} 次测试...")
        
        # 记录HTTP请求开始时间
        start_time = time.time()
        
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {'prompt': prompt}
                
                response = requests.post(
                    f"{server_url}/analyze",
                    files=files,
                    data=data,
                    timeout=60
                )
            
            # 记录HTTP请求结束时间
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                processing_time = result.get('processing_time_seconds', 0)
                
                response_times.append(response_time)
                processing_times.append(processing_time)
                
                print(f"  HTTP响应时间: {response_time:.3f}s")
                print(f"  模型处理时间: {processing_time:.3f}s")
                print(f"  结果长度: {len(result.get('result', ''))}")
            else:
                print(f"  错误: HTTP {response.status_code}")
                print(f"  响应: {response.text}")
                
        except Exception as e:
            print(f"  异常: {str(e)}")
        
        print()
    
    # 统计结果
    if response_times and processing_times:
        print("=" * 50)
        print("性能测试结果:")
        print(f"HTTP响应时间 (秒):")
        print(f"  平均值: {statistics.mean(response_times):.3f}")
        print(f"  中位数: {statistics.median(response_times):.3f}")
        print(f"  最小值: {min(response_times):.3f}")
        print(f"  最大值: {max(response_times):.3f}")
        if len(response_times) > 1:
            print(f"  标准差: {statistics.stdev(response_times):.3f}")
        
        print(f"\n模型处理时间 (秒):")
        print(f"  平均值: {statistics.mean(processing_times):.3f}")
        print(f"  中位数: {statistics.median(processing_times):.3f}")
        print(f"  最小值: {min(processing_times):.3f}")
        print(f"  最大值: {max(processing_times):.3f}")
        if len(processing_times) > 1:
            print(f"  标准差: {statistics.stdev(processing_times):.3f}")
        
        # 计算优化效果（与9秒基准比较）
        baseline_time = 9.0  # 原始响应时间
        avg_processing_time = statistics.mean(processing_times)
        improvement = ((baseline_time - avg_processing_time) / baseline_time) * 100
        
        print(f"\n性能改进:")
        print(f"  基准时间: {baseline_time:.3f}s")
        print(f"  优化后平均时间: {avg_processing_time:.3f}s")
        if improvement > 0:
            print(f"  性能提升: {improvement:.1f}%")
        else:
            print(f"  性能下降: {abs(improvement):.1f}%")
    else:
        print("没有有效的测试结果")

def main():
    parser = argparse.ArgumentParser(description='图片分析性能测试')
    parser.add_argument('--server', default='http://localhost:8207', 
                       help='服务器地址 (默认: http://localhost:8207)')
    parser.add_argument('--image', required=True, help='测试图片路径')
    parser.add_argument('--prompt', default='请详细描述这张图片的内容', 
                       help='分析提示词')
    parser.add_argument('--runs', type=int, default=5, help='测试次数 (默认: 5)')
    
    args = parser.parse_args()
    
    # 检查图片文件是否存在
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"错误: 图片文件不存在: {image_path}")
        return 1
    
    # 检查服务器是否可达
    try:
        response = requests.get(f"{args.server}/health", timeout=10)
        if response.status_code != 200:
            print(f"错误: 服务器健康检查失败: {response.status_code}")
            return 1
    except Exception as e:
        print(f"错误: 无法连接到服务器: {str(e)}")
        return 1
    
    benchmark_analyze(args.server, args.image, args.prompt, args.runs)
    return 0

if __name__ == "__main__":
    exit(main())