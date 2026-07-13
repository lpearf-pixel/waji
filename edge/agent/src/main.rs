use anyhow::Result;
use rumqttc::{AsyncClient, MqttOptions, QoS};
use serde::Serialize;
use std::{env, time::Duration};
use tokio::time;

#[derive(Serialize)]
struct Heartbeat<'a> {
    device_id: &'a str,
    status: &'a str,
    agent_version: &'a str,
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt::init();

    let device_id = env::var("DEVICE_ID").unwrap_or_else(|_| "local-edge-001".into());
    let mqtt_host = env::var("MQTT_HOST").unwrap_or_else(|_| "localhost".into());
    let mqtt_port = env::var("MQTT_PORT")
        .ok()
        .and_then(|value| value.parse().ok())
        .unwrap_or(1883);

    let mut options = MqttOptions::new(&device_id, mqtt_host, mqtt_port);
    options.set_keep_alive(Duration::from_secs(30));
    let (client, mut event_loop) = AsyncClient::new(options, 10);

    tokio::spawn(async move {
        loop {
            if let Err(error) = event_loop.poll().await {
                tracing::warn!(?error, "mqtt connection event failed");
                time::sleep(Duration::from_secs(2)).await;
            }
        }
    });

    let topic = format!("waji/devices/{device_id}/status");
    loop {
        let payload = serde_json::to_vec(&Heartbeat {
            device_id: &device_id,
            status: "online",
            agent_version: env!("CARGO_PKG_VERSION"),
        })?;
        client.publish(&topic, QoS::AtLeastOnce, false, payload).await?;
        time::sleep(Duration::from_secs(10)).await;
    }
}
