# 分支策略

## 长期分支

- `main`：生产稳定分支，必须通过 PR 和检查。
- `develop`：下一版本集成分支。

## 当前功能分支

- `feature/platform-backend`
- `feature/audio-ai`
- `feature/edge-agent`
- `feature/web-console`
- `feature/data-pipeline`

功能分支从 `develop` 创建，并合回 `develop`。

## 临时分支

- `release/vX.Y.Z`：发布候选，只允许修复、文档和版本调整。
- `hotfix/<description>`：从 `main` 分出，修复后同时合回 `main` 与 `develop`。

## 合并要求

- PR 描述写明范围、验证方式、风险和回滚方式。
- 禁止将数据文件、录音、模型权重和密钥提交到 Git。
- 优先 squash 合并功能分支，发布分支可保留合并提交。
