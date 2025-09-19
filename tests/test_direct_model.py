#!/usr/bin/env python3
"""
直接测试MiniCPM-V模型的推理能力
"""
import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model():
    # 创建一个简单的测试图片
    test_image = Image.new('RGB', (224, 224), color='red')
    
    model_path = '/app/models/MiniCPM-V-4_5-int4'
    logger.info(f"Loading model from {model_path}")
    
    try:
        # 加载模型和tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModel.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        ).eval()
        
        logger.info("Model loaded successfully")
        
        # 测试不同的消息格式
        test_cases = [
            # 格式1: 官方cookbook格式
            {
                'name': 'Official cookbook format',
                'msgs': [{'role': 'user', 'content': [test_image, 'What color is this image?']}],
                'params': {'sampling': False, 'max_new_tokens': 100}
            },
            # 格式2: 简化格式
            {
                'name': 'Simplified format',
                'msgs': [{'role': 'user', 'content': [test_image, 'Describe this image']}],
                'params': {}
            },
            # 格式3: 带system prompt
            {
                'name': 'With system prompt',
                'msgs': [
                    {'role': 'system', 'content': 'You are a helpful assistant that describes images.'},
                    {'role': 'user', 'content': [test_image, 'What do you see?']}
                ],
                'params': {'sampling': False}
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"\n=== Testing: {test_case['name']} ===")
            try:
                result = model.chat(
                    msgs=test_case['msgs'],
                    tokenizer=tokenizer,
                    **test_case['params']
                )
                logger.info(f"Result: {result}")
                logger.info(f"Result type: {type(result)}")
                
                if result and result != '<CLS>':
                    logger.info("✅ Success! Got meaningful response")
                    return True
                else:
                    logger.warning("⚠️ Got CLS or empty response")
                    
            except Exception as e:
                logger.error(f"❌ Error in {test_case['name']}: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False

if __name__ == '__main__':
    success = test_model()
    if success:
        print("✅ At least one test case succeeded")
    else:
        print("❌ All test cases failed")