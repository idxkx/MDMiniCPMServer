#!/usr/bin/env python3
"""
调试MiniCPM-V推理问题的脚本
"""

import os
import sys
import logging
from pathlib import Path
from PIL import Image
import torch
from transformers import AutoModel, AutoTokenizer

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_inference():
    """测试推理流程"""
    model_path = Path('./models/MiniCPM-V-4-int4')
    
    logger.info(f"Loading model from: {model_path}")
    
    # 加载tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        str(model_path),
        trust_remote_code=True
    )
    
    # 加载模型
    model = AutoModel.from_pretrained(
        str(model_path),
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    
    model.eval()
    
    logger.info("Model loaded successfully")
    
    # 创建测试图片 - 简单的红色方块
    image = Image.new('RGB', (224, 224), color=(255, 0, 0))
    
    # 测试1：最简单的调用
    logger.info("Testing simple call...")
    try:
        result = model.chat(
            image=image,
            msgs=[{"role": "user", "content": "Describe the image"}],
            tokenizer=tokenizer
        )
        logger.info(f"Simple call result: {repr(result)}")
    except Exception as e:
        logger.error(f"Simple call failed: {e}")
    
    # 测试2：禁用采样
    logger.info("Testing with sampling disabled...")
    try:
        result = model.chat(
            image=image,
            msgs=[{"role": "user", "content": "What color is this image?"}],
            tokenizer=tokenizer,
            sampling=False
        )
        logger.info(f"No sampling result: {repr(result)}")
    except Exception as e:
        logger.error(f"No sampling failed: {e}")
    
    # 测试3：更详细的参数
    logger.info("Testing with detailed parameters...")
    try:
        result = model.chat(
            image=image,
            msgs=[{"role": "user", "content": "Please describe this red image"}],
            tokenizer=tokenizer,
            sampling=False,
            max_new_tokens=50,
            do_sample=False
        )
        logger.info(f"Detailed params result: {repr(result)}")
    except Exception as e:
        logger.error(f"Detailed params failed: {e}")
    
    # 测试4：检查模型的内部方法
    logger.info("Checking model methods...")
    methods = [attr for attr in dir(model) if not attr.startswith('_')]
    logger.info(f"Available methods: {methods[:10]}...")  # 只显示前10个
    
    # 测试5：检查是否有generate方法
    if hasattr(model, 'generate'):
        logger.info("Model has generate method")
        try:
            # 尝试直接使用generate
            inputs = model.process_prompt(
                image=image,
                msgs=[{"role": "user", "content": "What is this?"}],
                tokenizer=tokenizer
            )
            logger.info("Process prompt successful")
        except Exception as e:
            logger.error(f"Process prompt failed: {e}")

if __name__ == "__main__":
    test_inference()