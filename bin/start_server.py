#!/usr/bin/env python3
"""
启动MiniCPM-V服务器
"""
import subprocess
import time
import requests
import os
import sys

def check_port_available(port):
    """检查端口是否可用"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def start_server(host="10.10.6.197", port=8207):
    """启动服务器"""
    # 检查端口是否被占用
    if not check_port_available(port):
        print(f"❌ 端口 {port} 已被占用")
        
        # 尝试连接现有服务并检查类型
        try:
            response = requests.get(f"http://{host}:{port}/health", timeout=5)
            service_info = response.json()
            
            if service_info.get('service') == 'MiniCPM-V Server':
                print("✅ MiniCPM-V服务已在运行")
                return True
            else:
                print(f"⚠️  端口被其他服务占用: {service_info}")
                # 尝试使用不同端口
                for try_port in [8208, 8209, 8210, 8211, 8212, 8213]:
                    if check_port_available(try_port):
                        print(f"尝试使用端口 {try_port}")
                        return start_server_on_port(host, try_port)
                        
                print("❌ 无法找到可用端口")
                return False
                
        except Exception as e:
            print(f"⚠️  无法连接到现有服务: {e}")
            return False
    
    return start_server_on_port(host, port)

def start_server_on_port(host, port):
    """在指定端口启动服务器"""
    print(f"🚀 在 {host}:{port} 启动MiniCPM-V服务器...")
    
    env = os.environ.copy()
    env['PYTHONPATH'] = 'src'
    
    try:
        # 启动服务器
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'main:app',
            '--host', '0.0.0.0',
            '--port', str(port)
        ], 
        cwd='/home/litata/xuke/MDMiniCPMServer',
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
        
        # 等待服务启动
        print("等待服务启动...")
        for i in range(10):
            time.sleep(2)
            try:
                response = requests.get(f"http://{host}:{port}/health", timeout=2)
                if response.status_code == 200:
                    service_info = response.json()
                    if service_info.get('service') == 'MiniCPM-V Server':
                        print(f"✅ 服务启动成功! 地址: http://{host}:{port}")
                        return True
            except:
                continue
        
        print("❌ 服务启动超时")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def load_default_model(host, port):
    """加载默认模型"""
    print("正在加载默认模型...")
    try:
        response = requests.post(
            f"http://{host}:{port}/load-model",
            json={"model_name": "MiniCPM-V-4_5-int4"},
            timeout=120
        )
        if response.status_code == 200:
            print("✅ 默认模型加载成功!")
            return True
        else:
            print(f"⚠️  模型加载失败: {response.text}")
            return False
    except Exception as e:
        print(f"⚠️  模型加载异常: {e}")
        return False

def test_service(host, port):
    """测试服务"""
    print("🧪 测试服务功能...")
    
    try:
        # 测试模型列表
        response = requests.get(f"http://{host}:{port}/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ 发现 {models['count']} 个模型")
            
            current_model = models.get('current_model')
            if current_model:
                print(f"当前模型: {current_model}")
            
            return True
        else:
            print(f"❌ 测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("MiniCPM-V 服务器启动工具")
    print("=" * 50)
    
    host = "10.10.6.197"
    port = 8207
    
    # 启动服务器
    if start_server(host, port):
        # 如果端口不是8207，询问最终使用的端口
        try:
            response = requests.get(f"http://{host}:8207/health", timeout=2)
            if response.status_code == 200 and response.json().get('service') == 'MiniCPM-V Server':
                final_port = 8207
            else:
                # 查找实际端口
                for try_port in [8208, 8209, 8210, 8211, 8212, 8213]:
                    try:
                        response = requests.get(f"http://{host}:{try_port}/health", timeout=2)
                        if response.status_code == 200 and response.json().get('service') == 'MiniCPM-V Server':
                            final_port = try_port
                            break
                    except:
                        continue
                else:
                    final_port = port
        except:
            final_port = port
        
        # 加载模型和测试
        load_default_model(host, final_port)
        test_service(host, final_port)
        
        print(f"\n🎉 服务就绪!")
        print(f"服务地址: http://{host}:{final_port}")
        print(f"API文档: http://{host}:{final_port}/docs")
        print(f"健康检查: curl http://{host}:{final_port}/health")
    else:
        print("\n💥 启动失败")