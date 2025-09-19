#!/usr/bin/env python3
"""
部署脚本 - 更新运行中的服务
"""
import requests
import time
import subprocess
import os
import signal

def check_service_status(host="10.10.6.197", port=8207):
    """检查服务状态"""
    try:
        response = requests.get(f"http://{host}:{port}/health", timeout=5)
        return response.json()
    except:
        return None

def deploy_service():
    """部署服务"""
    print("🚀 开始部署MiniCPM-V服务...")
    
    # 检查当前服务状态
    current_status = check_service_status()
    if current_status:
        print(f"当前服务状态: {current_status}")
        
        # 检查是否是新版本
        if current_status.get('service') == 'MiniCPM-V Server':
            print("✅ 新版本服务已在运行")
            return True
        else:
            print("⚠️  发现旧版本服务，需要更新")
    
    # 启动新服务进程
    print("正在启动新服务...")
    
    env = os.environ.copy()
    env['PYTHONPATH'] = 'src'
    
    try:
        # 尝试启动服务
        process = subprocess.Popen([
            'python', '-m', 'uvicorn', 'main:app',
            '--host', '0.0.0.0',
            '--port', '8207',
            '--workers', '1'
        ], 
        cwd='/home/litata/xuke/MDMiniCPMServer',
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
        
        # 等待服务启动
        print("等待服务启动...")
        time.sleep(10)
        
        # 检查服务是否启动成功
        status = check_service_status()
        if status and status.get('service') == 'MiniCPM-V Server':
            print("✅ 新服务启动成功！")
            
            # 加载默认模型
            print("正在加载默认模型...")
            try:
                response = requests.post(
                    "http://10.10.6.197:8207/load-model",
                    json={"model_name": "MiniCPM-V-4_5-int4"},
                    timeout=60
                )
                if response.status_code == 200:
                    print("✅ 默认模型加载成功！")
                else:
                    print(f"⚠️  模型加载失败: {response.text}")
            except Exception as e:
                print(f"⚠️  模型加载异常: {e}")
            
            return True
        else:
            print("❌ 服务启动失败")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ 启动过程出错: {e}")
        return False

def test_service():
    """测试服务功能"""
    print("\n🧪 测试服务功能...")
    
    # 测试健康检查
    status = check_service_status()
    if not status:
        print("❌ 健康检查失败")
        return False
    
    print(f"✅ 健康检查通过: {status}")
    
    # 测试模型列表
    try:
        response = requests.get("http://10.10.6.197:8207/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ 模型列表获取成功: {models['count']} 个模型")
            
            # 显示当前模型状态
            current_model = models.get('current_model')
            if current_model:
                print(f"当前加载模型: {current_model}")
            else:
                print("当前没有加载任何模型")
                
            return True
        else:
            print(f"❌ 模型列表获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("MiniCPM-V Server 部署工具")
    print("=" * 50)
    
    success = deploy_service()
    if success:
        test_success = test_service()
        if test_success:
            print("\n🎉 部署和测试完成！")
            print(f"服务地址: http://10.10.6.197:8207")
            print("API文档: http://10.10.6.197:8207/docs")
        else:
            print("\n⚠️  部署完成但测试失败")
    else:
        print("\n💥 部署失败")