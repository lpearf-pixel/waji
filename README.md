# Waji

Waji 是面向挖掘机、装载机和铲车等工程机械的现场采集、人工诊断与维修证据闭环平台。

## 当前成熟度路线

项目不以固定边缘盒起步，按阶段推进：

1. **Gate 0：故障触发式现场采集**——手机系统录音机录音，通过手机网页上传；记录工况、位置、老师傅 Hypothesis、人工 Decision、检查/维修 Outcome 和维修后复测。
2. **Gate 1–4：案例与低成本便携终端**——先用真实闭环案例验证流程和证据价值，再设计人民币 1,000–2,500 元的模块化便携终端。
3. **Gate 5 之后：固定边缘小规模试点**——只有证明持续高价值前兆、人工采集不足且全生命周期经济性为正，才进入固定监测。

老师傅听音、频谱、相似案例、规则和模型输出都先记录为 `Hypothesis`。检查、测试、维修、排除或可重复复测证据才能形成 `Outcome`。

## Gate 0 功能

- Django账号登录和手机响应式网页；
- 设备和故障事件台账；
- 上传手机录制的 WAV、M4A、MP3、AAC、OGG、3GP；
- 原始录音不可替换，保存 SHA-256；
- 记录录音部位、位置、距离、方向、动作、负载、转速、重复序号和现场杂音；
- 检测静音、明显削波和解码失败；
- 生成独立的轻度去噪 WAV 试听副本，并保存算法与参数清单；
- 分开记录 `Observation`、`Hypothesis`、`Decision`、`Outcome`；
- 自动显示 `incomplete`、`complete`、`verified_complete`；
- 原始录音和轻度去噪副本可分别试听。

轻度去噪版只用于辅助试听，不能替代原始证据，也不能单独确认故障。

## 当前不包含

- 浏览器直接录音或原生App；
- 自动确认故障、自动停机、自动拆机或自动换件；
- CAN读写；
- VMD或深度学习去噪的生产部署；
- 固定边缘批量安装；
- 故障诊断准确率声明。

## 技术架构

- 管理与手机网页：Django + Django REST Framework；
- 音频基础处理：NumPy + FFmpeg；
- 数据库：开发可用SQLite，部署使用PostgreSQL；
- 文件：开发使用Django本地媒体存储，数据模型预留S3/MinIO迁移；
- AI服务：FastAPI；
- 固定边缘实验代码：Rust，当前不属于Gate 0产品入口；
- CI：GitHub Actions。

## Docker启动

```bash
cp .env.example .env
docker compose up --build
```

首次启动后创建管理员账号：

```bash
docker compose exec platform python manage.py createsuperuser
```

入口：

- 手机现场采集：`http://localhost:8000/field/`
- Django管理台：`http://localhost:8000/admin/`
- 平台健康检查：`http://localhost:8000/api/v1/health/`
- API文档：`http://localhost:8000/api/docs/`
- AI服务健康检查：`http://localhost:8100/health`
- MinIO控制台：`http://localhost:9001`

## 不使用Docker的本地启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r apps/platform/requirements.txt
python apps/platform/manage.py migrate
python apps/platform/manage.py createsuperuser
DJANGO_DEBUG=1 python apps/platform/manage.py runserver
```

打开 `http://127.0.0.1:8000/field/`。

手机访问同一局域网中的电脑时，需要把电脑IP加入 `DJANGO_ALLOWED_HOSTS`，并使用电脑的局域网地址，例如 `http://192.168.1.20:8000/field/`。

## 验证

```bash
python apps/platform/manage.py check
python apps/platform/manage.py makemigrations --check --dry-run
python apps/platform/manage.py test core.tests -v 2
python -m compileall services/audio_ai/app
cargo check --manifest-path edge/agent/Cargo.toml
python -m unittest tests.skills.test_waji_skills -v
```

Gate 0现场演练步骤见 `docs/gate0-rehearsal.md`。

## 分支

- `main`：稳定、可发布代码；
- `develop`：日常集成分支；
- 功能开发从 `develop` 分支开始，通过PR合回。
