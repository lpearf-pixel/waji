use anyhow::Result;
use chrono::Utc;
use clap::Parser;
use std::path::PathBuf;
use tokio::{
    signal,
    time::{self, Duration},
};
use tracing_subscriber::EnvFilter;
use waji_edge_agent::{
    config::Config,
    model::{AlertEvent, UploadEvent},
    mqtt::MqttPublisher,
    pipeline::compute_features,
    source::{SimulatorSource, VibrationSource},
    storage::{PendingRecord, Spool},
    uploader::S3Uploader,
};

#[derive(Debug, Parser)]
#[command(version, about)]
struct Cli {
    #[arg(
        long,
        env = "WAJI_CONFIG",
        default_value = "config/edge.example.toml"
    )]
    config: PathBuf,
    #[arg(long, help = "Capture one window, attempt upload, then exit")]
    once: bool,
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info")),
        )
        .init();

    let cli = Cli::parse();
    let config = Config::load(&cli.config)?;
    let spool = Spool::new(&config.spool.root_dir, config.spool.keep_uploaded)?;
    let uploader = S3Uploader::new(&config.s3)?;
    let mqtt = MqttPublisher::connect(&config);
    let mut source = SimulatorSource::new(config.source.clone());

    if let Err(error) = mqtt.publish_status("online").await {
        tracing::warn!(?error, "failed to queue online status");
    }
    drain_pending(&spool, &uploader, &mqtt).await;

    loop {
        let window = source.next_window()?;
        let features = compute_features(
            &window.samples,
            window.sample_rate_hz,
            &config.pipeline,
        );
        let record = spool.persist(&config, &window, features.clone())?;
        tracing::info!(
            batch_id = %record.metadata.batch_id,
            sample_count = record.metadata.sample_count,
            anomaly_score = record.metadata.features.anomaly_score,
            simulated_fault = record.metadata.simulated_fault,
            "vibration window persisted"
        );

        if let Err(error) = mqtt
            .publish_features(&config.sensor.id, &features)
            .await
        {
            tracing::warn!(?error, "failed to publish features");
        }
        if features.anomaly_score >= config.pipeline.alert_threshold {
            let alert = AlertEvent {
                batch_id: &record.metadata.batch_id,
                sensor_id: &record.metadata.sensor_id,
                sensor_position: &record.metadata.sensor_position,
                anomaly_score: features.anomaly_score,
                algorithm: &features.algorithm,
                timestamp: Utc::now(),
            };
            if let Err(error) = mqtt.publish_alert(&alert).await {
                tracing::warn!(?error, "failed to publish alert");
            }
        }

        upload_one(&spool, &uploader, &mqtt, &record).await;
        drain_pending(&spool, &uploader, &mqtt).await;

        if cli.once {
            break;
        }

        tokio::select! {
            _ = time::sleep(Duration::from_secs(config.source.publish_interval_seconds)) => {}
            _ = signal::ctrl_c() => {
                tracing::info!("shutdown signal received");
                break;
            }
        }
    }

    if let Err(error) = mqtt.publish_status("offline").await {
        tracing::warn!(?error, "failed to queue offline status");
    }
    Ok(())
}

async fn drain_pending(spool: &Spool, uploader: &S3Uploader, mqtt: &MqttPublisher) {
    match spool.list_pending() {
        Ok(records) => {
            for record in records.into_iter().take(20) {
                upload_one(spool, uploader, mqtt, &record).await;
            }
        }
        Err(error) => tracing::warn!(?error, "failed to scan pending spool"),
    }
}

async fn upload_one(
    spool: &Spool,
    uploader: &S3Uploader,
    mqtt: &MqttPublisher,
    record: &PendingRecord,
) {
    match uploader.upload(record).await {
        Ok(()) => {
            let event = UploadEvent {
                batch_id: &record.metadata.batch_id,
                data_object_key: &record.metadata.data_object_key,
                metadata_object_key: &record.metadata.metadata_object_key,
                timestamp: Utc::now(),
            };
            if let Err(error) = mqtt.publish_upload(&event).await {
                tracing::warn!(?error, "failed to publish upload event");
            }
            if let Err(error) = spool.mark_uploaded(record) {
                tracing::error!(
                    ?error,
                    "uploaded data but failed to update local spool state"
                );
            } else {
                tracing::info!(batch_id = %record.metadata.batch_id, "batch uploaded");
            }
        }
        Err(error) => tracing::warn!(
            batch_id = %record.metadata.batch_id,
            ?error,
            "upload failed; batch remains queued"
        ),
    }
}
