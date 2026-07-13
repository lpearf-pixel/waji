use crate::{
    config::Config,
    model::{BatchMetadata, VibrationFeatures, VibrationWindow},
};
use anyhow::{Context, Result};
use flate2::{write::GzEncoder, Compression};
use sha2::{Digest, Sha256};
use std::{
    fs,
    io::Write,
    path::{Path, PathBuf},
};
use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct PendingRecord {
    pub metadata: BatchMetadata,
    pub batch_dir: PathBuf,
    pub data_path: PathBuf,
    pub metadata_path: PathBuf,
}

#[derive(Clone)]
pub struct Spool {
    root: PathBuf,
    keep_uploaded: bool,
}

impl Spool {
    pub fn new(root: impl AsRef<Path>, keep_uploaded: bool) -> Result<Self> {
        let root = root.as_ref().to_path_buf();
        fs::create_dir_all(root.join("pending"))?;
        fs::create_dir_all(root.join("uploaded"))?;
        Ok(Self {
            root,
            keep_uploaded,
        })
    }

    pub fn persist(
        &self,
        config: &Config,
        window: &VibrationWindow,
        features: VibrationFeatures,
    ) -> Result<PendingRecord> {
        let batch_id = Uuid::new_v4().to_string();
        let date_prefix = window.started_at.format("%Y/%m/%d");
        let base_key = format!(
            "devices/{}/vibration/{}/{}/{}",
            config.device.id, config.sensor.id, date_prefix, batch_id
        );
        let data_object_key = format!("{base_key}.csv.gz");
        let metadata_object_key = format!("{base_key}.json");

        let compressed = encode_csv(window)?;
        let data_sha256 = format!("{:x}", Sha256::digest(&compressed));
        let duration_seconds = window.samples.len() as f32 / window.sample_rate_hz as f32;
        let metadata = BatchMetadata {
            schema_version: "waji.vibration.batch.v1".into(),
            batch_id: batch_id.clone(),
            device_id: config.device.id.clone(),
            machine_type: config.device.machine_type.clone(),
            machine_model: config.device.machine_model.clone(),
            sensor_id: config.sensor.id.clone(),
            sensor_position: config.sensor.position.clone(),
            sensor_orientation: config.sensor.orientation.clone(),
            source_kind: config.source.kind.clone(),
            started_at: window.started_at,
            duration_seconds,
            sample_rate_hz: window.sample_rate_hz,
            sample_count: window.samples.len(),
            data_object_key,
            metadata_object_key,
            data_sha256,
            simulated_fault: window.simulated_fault,
            features,
        };

        let pending_root = self.root.join("pending");
        let temp_dir = pending_root.join(format!(".tmp-{batch_id}"));
        let batch_dir = pending_root.join(&batch_id);
        fs::create_dir(&temp_dir)?;
        let data_path = temp_dir.join("data.csv.gz");
        let metadata_path = temp_dir.join("metadata.json");
        atomic_write(&data_path, &compressed)?;
        atomic_write(&metadata_path, &serde_json::to_vec_pretty(&metadata)?)?;
        fs::rename(&temp_dir, &batch_dir)?;

        Ok(PendingRecord {
            metadata,
            data_path: batch_dir.join("data.csv.gz"),
            metadata_path: batch_dir.join("metadata.json"),
            batch_dir,
        })
    }

    pub fn list_pending(&self) -> Result<Vec<PendingRecord>> {
        let mut records = Vec::new();
        for entry in fs::read_dir(self.root.join("pending"))? {
            let batch_dir = entry?.path();
            if !batch_dir.is_dir()
                || batch_dir
                    .file_name()
                    .and_then(|value| value.to_str())
                    .is_some_and(|name| name.starts_with(".tmp-"))
            {
                continue;
            }
            let metadata_path = batch_dir.join("metadata.json");
            let data_path = batch_dir.join("data.csv.gz");
            if !metadata_path.exists() || !data_path.exists() {
                tracing::warn!(path = %batch_dir.display(), "ignoring incomplete spool batch");
                continue;
            }
            let metadata: BatchMetadata = serde_json::from_slice(&fs::read(&metadata_path)?)
                .with_context(|| format!("invalid spool metadata {}", metadata_path.display()))?;
            records.push(PendingRecord {
                metadata,
                batch_dir,
                data_path,
                metadata_path,
            });
        }
        records.sort_by_key(|record| record.metadata.started_at);
        Ok(records)
    }

    pub fn mark_uploaded(&self, record: &PendingRecord) -> Result<()> {
        if self.keep_uploaded {
            fs::rename(
                &record.batch_dir,
                self.root.join("uploaded").join(&record.metadata.batch_id),
            )?;
        } else {
            fs::remove_dir_all(&record.batch_dir)?;
        }
        Ok(())
    }
}

fn encode_csv(window: &VibrationWindow) -> Result<Vec<u8>> {
    let encoder = GzEncoder::new(Vec::new(), Compression::default());
    let mut writer = csv::WriterBuilder::new()
        .has_headers(true)
        .from_writer(encoder);
    writer.write_record(["sample_index", "x_g", "y_g", "z_g"])?;
    for (index, sample) in window.samples.iter().enumerate() {
        writer.serialize((index, sample.x_g, sample.y_g, sample.z_g))?;
    }
    let encoder = writer.into_inner()?;
    Ok(encoder.finish()?)
}

fn atomic_write(path: &Path, bytes: &[u8]) -> Result<()> {
    let temp_path = path.with_extension(format!(
        "{}.tmp",
        path.extension()
            .and_then(|value| value.to_str())
            .unwrap_or("data")
    ));
    let mut file = fs::File::create(&temp_path)?;
    file.write_all(bytes)?;
    file.sync_all()?;
    fs::rename(temp_path, path)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        config::{
            DeviceConfig, MqttConfig, PipelineConfig, S3Config, SensorConfig, SourceConfig,
            SpoolConfig,
        },
        model::{AxisFeatures, VibrationSample},
    };
    use chrono::Utc;
    use tempfile::tempdir;

    fn config(root: &str) -> Config {
        Config {
            device: DeviceConfig {
                id: "EX-1".into(),
                machine_type: "excavator".into(),
                machine_model: "test".into(),
            },
            sensor: SensorConfig {
                id: "VIB-1".into(),
                position: "pump".into(),
                orientation: "x_forward".into(),
            },
            mqtt: MqttConfig {
                host: "localhost".into(),
                port: 1883,
                username: None,
                password: None,
                tls: false,
            },
            s3: S3Config {
                endpoint: "http://localhost:9000".into(),
                region: "us-east-1".into(),
                bucket: "test".into(),
                access_key: "a".into(),
                secret_key: "b".into(),
                path_style: true,
            },
            spool: SpoolConfig {
                root_dir: root.into(),
                keep_uploaded: true,
                retention_days: 14,
            },
            source: SourceConfig {
                kind: "simulator".into(),
                sample_rate_hz: 100,
                window_seconds: 1.0,
                publish_interval_seconds: 1,
                anomaly_every_windows: 10,
                seed: 1,
            },
            pipeline: PipelineConfig::default(),
        }
    }

    #[test]
    fn persists_and_atomically_moves_record() {
        let dir = tempdir().unwrap();
        let cfg = config(dir.path().to_str().unwrap());
        let spool = Spool::new(&cfg.spool.root_dir, true).unwrap();
        let window = VibrationWindow {
            started_at: Utc::now(),
            sample_rate_hz: 100,
            samples: vec![
                VibrationSample {
                    x_g: 0.1,
                    y_g: 0.2,
                    z_g: 1.0,
                };
                100
            ],
            simulated_fault: false,
        };
        let features = VibrationFeatures {
            algorithm: "test".into(),
            x: dummy_axis(),
            y: dummy_axis(),
            z: dummy_axis(),
            vector_rms_g: 0.1,
            anomaly_score: 0.0,
        };
        let record = spool.persist(&cfg, &window, features).unwrap();
        assert_eq!(spool.list_pending().unwrap().len(), 1);
        spool.mark_uploaded(&record).unwrap();
        assert!(spool.list_pending().unwrap().is_empty());
        assert!(dir
            .path()
            .join("uploaded")
            .join(record.metadata.batch_id)
            .exists());
    }

    fn dummy_axis() -> AxisFeatures {
        AxisFeatures {
            mean_g: 0.0,
            rms_g: 0.0,
            std_dev_g: 0.0,
            peak_abs_g: 0.0,
            peak_to_peak_g: 0.0,
            kurtosis: 0.0,
            crest_factor: 0.0,
            dominant_frequency_hz: 0.0,
        }
    }
}
