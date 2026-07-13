# Waji

工程机械 AI 听诊与异常预警平台，面向挖掘机、装载机、铲车等设备。

## 第一阶段目标

- 管理设备、机型、采集点和运行工况
- 接收声音与传感器数据
- 输出异常分数、疑似部位和风险等级
- 保存维修确认结果，形成可持续训练的数据闭环
- 支持边缘端断网缓存和恢复上传

## 技术架构

- 管理平台：Django + Django REST Framework
- AI 服务：FastAPI + PyTorch/音频处理组件
- 边缘采集：Rust
- 消息通道：MQTT
- 任务队列：Celery + Redis
- 数据库：PostgreSQL
- 文件存储：MinIO/S3
- Web 控制台：React，后续在独立功能分支实现

## 快速启动

```bash
cp .env.example .env
docker compose up --build
```

启动后：

- 平台健康检查：`http://localhost:8000/api/v1/health/`
- 平台 API 文档：`http://localhost:8000/api/docs/`
- AI 服务健康检查：`http://localhost:8100/health`
- MinIO 控制台：`http://localhost:9001`

## 分支

- `main`：稳定、可发布代码
- `develop`：日常集成分支
- `feature/platform-backend`：Django/DRF 管理平台
- `feature/audio-ai`：声音异常检测与诊断模型
- `feature/edge-agent`：边缘采集代理
- `feature/web-console`：Web 管理端
- `feature/data-pipeline`：数据清洗、标注、数据集与训练流水线

详细说明见 `docs/`。
