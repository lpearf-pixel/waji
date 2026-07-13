use crate::{
    config::Config,
    model::{AlertEvent, DeviceStatus, UploadEvent, VibrationFeatures},
};
use anyhow::Result;
use chrono::Utc;
use rumqttc::{AsyncClient, LastWill, MqttOptions, QoS, Transport};
use serde::Serialize;
use std::time::Duration;
use tokio::time;

#[derive(Clone)]
pub struct MqttPublisher {
    client: AsyncClient,
    device_id: String,
}

impl MqttPublisher {
    pub fn connect(config: &Config) -> Self {
        let client_id = format!("waji-edge-{}", config.device.id);
        let mut options = MqttOptions::new(
            client_id,
            config.mqtt.host.clone(),
            config.mqtt.port,
        );
        options.set_keep_alive(Duration::from_secs(30));
        if let (Some(username), Some(password)) = (&config.mqtt.username, &config.mqtt.password) {
            options.set_credentials(username.as_str(), password.as_str());
        }
        if config.mqtt.tls {
            options.set_transport(Transport::tls_with_default_config());
        }
        options.set_last_will(LastWill::new(
            format!("waji/devices/{}/status", config.device.id),
            br#"{"status":"offline"}"#.to_vec(),
            QoS::AtLeastOnce,
            true,
        ));

        let (client, mut event_loop) = AsyncClient::new(options, 20);
        tokio::spawn(async move {
            loop {
                if let Err(error) = event_loop.poll().await {
                    tracing::warn!(?error, "mqtt event loop failed; retrying");
                    time::sleep(Duration::from_secs(2)).await;
                }
            }
        });
        Self {
            client,
            device_id: config.device.id.clone(),
        }
    }

    pub async fn publish_status(&self, status: &str) -> Result<()> {
        let event = DeviceStatus {
            device_id: &self.device_id,
            status,
            agent_version: env!("CARGO_PKG_VERSION"),
            timestamp: Utc::now(),
        };
        self.publish_json(
            &format!("waji/devices/{}/status", self.device_id),
            &event,
            true,
        )
        .await
    }

    pub async fn publish_features(
        &self,
        sensor_id: &str,
        features: &VibrationFeatures,
    ) -> Result<()> {
        self.publish_json(
            &format!(
                "waji/devices/{}/sensors/{sensor_id}/features",
                self.device_id
            ),
            features,
            false,
        )
        .await
    }

    pub async fn publish_upload(&self, event: &UploadEvent<'_>) -> Result<()> {
        self.publish_json(
            &format!("waji/devices/{}/uploads", self.device_id),
            event,
            false,
        )
        .await
    }

    pub async fn publish_alert(&self, event: &AlertEvent<'_>) -> Result<()> {
        self.publish_json(
            &format!("waji/devices/{}/alerts", self.device_id),
            event,
            false,
        )
        .await
    }

    async fn publish_json<T: Serialize>(
        &self,
        topic: &str,
        payload: &T,
        retain: bool,
    ) -> Result<()> {
        self.client
            .publish(
                topic,
                QoS::AtLeastOnce,
                retain,
                serde_json::to_vec(payload)?,
            )
            .await?;
        Ok(())
    }
}
