# Waji Edge Agent

边缘代理负责把传感器数据变成可追溯的数据批次，并在网络不稳定时安全缓存。当前版本已经跑通：

```text
模拟三轴振动 -> 10 秒窗口 -> RMS/峭度/峰值/FFT -> gzip CSV
             -> 本地 pending 队列 -> MinIO/S3 -> MQTT 特征、上传和告警事件
```

## 本地运行

先从仓库根目录启动基础设施：

```bash
cp .env.example .env
docker compose up --build minio minio-init mosquitto edge-agent
```

查看边缘日志：

```bash
docker compose logs -f edge-agent
```

MinIO 控制台为 `http://localhost:9001`。数据进入桶 `waji-audio`，对象结构为：

```text
devices/<device-id>/vibration/<sensor-id>/YYYY/MM/DD/<batch-id>.csv.gz
devices/<device-id>/vibration/<sensor-id>/YYYY/MM/DD/<batch-id>.json
```

也可以只执行一个窗口：

```bash
cargo run --manifest-path edge/agent/Cargo.toml -- \
  --config edge/agent/config/edge.example.toml --once
```

如果 MinIO 或 MQTT 不在线，原始批次仍保存在 `spool/pending`，下次启动继续上传。

## MQTT 主题

- `waji/devices/<device-id>/status`
- `waji/devices/<device-id>/sensors/<sensor-id>/features`
- `waji/devices/<device-id>/uploads`
- `waji/devices/<device-id>/alerts`

MQTT 只承载状态和小型 JSON，原始波形进入对象存储。

## 配置覆盖

配置文件中的常用部署参数可被环境变量覆盖：

- `WAJI_DEVICE_ID`
- `WAJI_MQTT_HOST`、`WAJI_MQTT_PORT`
- `WAJI_MQTT_USERNAME`、`WAJI_MQTT_PASSWORD`
- `WAJI_S3_ENDPOINT`、`WAJI_S3_BUCKET`
- `WAJI_S3_ACCESS_KEY`、`WAJI_S3_SECRET_KEY`
- `WAJI_SPOOL_DIR`

## 安装为 systemd 服务

```bash
sudo install -m 0755 target/release/waji-edge-agent /usr/local/bin/
sudo useradd --system --home /var/lib/waji --create-home waji || true
sudo install -d -o waji -g waji /etc/waji /var/lib/waji
sudo install -m 0640 config/edge.example.toml /etc/waji/edge.toml
sudo install -m 0644 deploy/waji-edge.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now waji-edge
```

正式机器端建议直接使用 systemd，以便后续访问 `/dev/spidev*`、ALSA、CAN 和 IIO 设备。

## 当前边界

- 数据源目前是确定性模拟器，用于验证端到端链路。
- `heuristic_v1` 异常分数只是工程联调阈值，不是故障诊断模型。
- 下一步新增 `Adxl355Source`，读取 SPI 传感器并输出相同的 `VibrationWindow`。
- 正式部署必须启用 MQTT TLS、设备级凭证、MinIO TLS 和密钥轮换。
