# MiniCPM-V API 使用指南

## 服务信息
- **地址**: `http://10.10.6.197:8207`
- **API文档**: `http://10.10.6.197:8207/docs`
- **健康检查**: `http://10.10.6.197:8207/health`

## API设计说明

### 核心理念
1. **模型统一管理**: 通过 `/load-model` 接口统一加载模型，分析接口不再需要指定模型
2. **简化调用**: 分析接口参数更简洁，只需图片和提示词
3. **状态透明**: 通过 `/models` 接口随时查看当前模型状态

## 接口列表

### 1. 健康检查
```bash
GET /health
curl http://10.10.6.197:8207/health
```

### 2. 查看模型状态
```bash
GET /models
curl http://10.10.6.197:8207/models
```
返回当前可用模型列表和已加载模型信息。

### 3. 加载模型 ⭐
```bash
POST /load-model
curl -X POST http://10.10.6.197:8207/load-model \
  -H "Content-Type: application/json" \
  -d '{"model_name": "MiniCPM-V-4_5-int4"}'
```

**可用模型**:
- `MiniCPM-V-4-int4`: 基础版本，较快推理速度
- `MiniCPM-V-4_5-int4`: 增强版本，更好的图片理解能力 (推荐)

### 4. 图片分析 - 文件上传
```bash
POST /analyze
curl -X POST http://10.10.6.197:8207/analyze \
  -F 'file=@your_image.jpg' \
  -F 'prompt=请详细描述这张图片的内容'
```

**参数**:
- `file`: 图片文件 (必需)
- `prompt`: 分析提示词 (可选，默认: "请详细描述这张图片的内容")

### 5. 图片分析 - URL
```bash
POST /analyze-url
curl -X POST http://10.10.6.197:8207/analyze-url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "prompt": "请描述图片内容"
  }'
```

## 使用流程

### 首次使用
1. 加载模型: `POST /load-model`
2. 分析图片: `POST /analyze` 或 `POST /analyze-url`

### 切换模型
1. 加载新模型: `POST /load-model` (会自动卸载旧模型)
2. 继续分析: `POST /analyze` 或 `POST /analyze-url`

### 检查状态
随时调用 `GET /models` 查看当前模型状态

## 示例响应

### 成功的图片分析
```json
{
  "status": "success",
  "result": "这张图片显示了一个美丽的乡村风景...",
  "model_used": "MiniCPM-V-4_5-int4",
  "prompt": "请描述图片内容",
  "filename": "test.jpg"
}
```

### 模型加载成功
```json
{
  "status": "success",
  "message": "Model MiniCPM-V-4_5-int4 loaded successfully"
}
```

### 错误响应
```json
{
  "detail": "没有已加载的模型，请先调用 /load-model 加载模型"
}
```

## 错误处理

### 常见错误
1. **没有加载模型**: 先调用 `/load-model`
2. **模型加载失败**: 检查模型名称是否正确
3. **图片格式错误**: 确保上传的是图片文件
4. **URL无法访问**: 确保图片URL可以公开访问

### 错误状态码
- `400`: 请求参数错误
- `500`: 服务器内部错误

## 最佳实践

1. **推荐模型**: 使用 `MiniCPM-V-4_5-int4` 获得最佳分析效果
2. **提示词优化**: 根据需求调整提示词，如"请详细描述这张图片中的人物、物体和场景"
3. **模型预热**: 服务启动后建议先加载模型进行预热
4. **超时设置**: 图片分析可能需要10-30秒，建议设置合适的超时时间

## 性能说明

- **模型加载时间**: 5-15秒
- **图片分析时间**: 3-15秒 (取决于图片复杂度和模型)
- **并发支持**: 建议单模型单请求，避免CUDA内存冲突
- **内存占用**: V4.5模型约6GB显存，V4模型约2.8GB显存