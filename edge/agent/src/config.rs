use anyhow::{bail, Context, Result};
use serde::Deserialize;
use std::{env, fs, path::Path};

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    pub device: DeviceConfig,
    pub sensor: SensorConfig,
    pub mqtt: MqttConfig,
    pub s3: S3Config,
    pub spool: SpoolConfig,
    pub source: SourceConfig,
    #[serde(default)]
    pub pipeline: PipelineConfig,
}

#[derive(Debug, Clone, Deserialize)]
pub struct DeviceConfig {
    pub id: String,
    pub machine_type: String,
    pub machine_model: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SensorConfig {
    pub id: String,
    pub position: String,
    pub orientation: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct MqttConfig {
    pub host: String,
    #[serde(default = "default_mqtt_port")]
    pub port: u16,
    pub username: Option<String>,
    pub password: Option<String>,
    #[serde(default)]
    pub tls: bool,
}

#[derive(Debug, Clone, Deserialize)]
pub struct S3Config {
    pub endpoint: String,
    #[serde(default = "default_region")]
    pub region: String,
    pub bucket: String,
    pub access_key: String,
    pub secret_key: String,
    #[serde(default = "default_true")]
    pub path_style: bool,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SpoolConfig {
    pub root_dir: String,
    #[serde(default = "default_true")]
    pub keep_uploaded: bool,
    #[serde(default = "default_retention_days")]
    pub retention_days: u32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SourceConfig {
    #[serde(default = "default_source_kind")]
    pub kind: String,
    #[serde(default = "default_sample_rate")]
    pub sample_rate_hz: u32,
    #[serde(default = "default_window_seconds")]
    pub window_seconds: f32,
    #[serde(default = "default_publish_interval")]
    pub publish_interval_seconds: u64,
    #[serde(default = "default_anomaly_every")]
    pub anomaly_every_windows: u64,
    #[serde(default = "default_seed")]
    pub seed: u64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct PipelineConfig {
    #[serde(default = "default_baseline_rms")]
    pub baseline_rms_g: f32,
    #[serde(default = "default_kurtosis_reference")]
    pub kurtosis_reference: f32,
    #[serde(default = "default_alert_threshold")]
    pub alert_threshold: f32,
}

impl Default for PipelineConfig {
    fn default() -> Self {
        Self {
            baseline_rms_g: default_baseline_rms(),
            kurtosis_reference: default_kurtosis_reference(),
            alert_threshold: default_alert_threshold(),
        }
    }
}

impl Config {
    pub fn load(path: impl AsRef<Path>) -> Result<Self> {
        let path = path.as_ref();
        let raw = fs::read_to_string(path)
            .with_context(|| format!("failed to read config {}", path.display()))?;
        let mut config: Self = toml::from_str(&raw)
            .with_context(|| format!("failed to parse config {}", path.display()))?;
        config.apply_env_overrides();
        config.validate()?;
        Ok(config)
    }

    fn apply_env_overrides(&mut self) {
        override_string("WAJI_DEVICE_ID", &mut self.device.id);
        override_string("WAJI_MQTT_HOST", &mut self.mqtt.host);
        override_u16("WAJI_MQTT_PORT", &mut self.mqtt.port);
        override_option("WAJI_MQTT_USERNAME", &mut self.mqtt.username);
        override_option("WAJI_MQTT_PASSWORD", &mut self.mqtt.password);
        override_string("WAJI_S3_ENDPOINT", &mut self.s3.endpoint);
        override_string("WAJI_S3_BUCKET", &mut self.s3.bucket);
        override_string("WAJI_S3_ACCESS_KEY", &mut self.s3.access_key);
        override_string("WAJI_S3_SECRET_KEY", &mut self.s3.secret_key);
        override_string("WAJI_SPOOL_DIR", &mut self.spool.root_dir);
    }

    fn validate(&self) -> Result<()> {
        if self.device.id.trim().is_empty() || self.sensor.id.trim().is_empty() {
            bail!("device.id and sensor.id must not be empty");
        }
        if self.source.sample_rate_hz < 10 {
            bail!("source.sample_rate_hz must be at least 10 Hz");
        }
        if !(0.1..=300.0).contains(&self.source.window_seconds) {
            bail!("source.window_seconds must be between 0.1 and 300 seconds");
        }
        if !(0.0..=1.0).contains(&self.pipeline.alert_threshold) {
            bail!("pipeline.alert_threshold must be between 0 and 1");
        }
        if self.source.kind != "simulator" {
            bail!(
                "unsupported source.kind '{}'; this release supports simulator",
                self.source.kind
            );
        }
        Ok(())
    }
}

fn override_string(name: &str, target: &mut String) {
    if let Ok(value) = env::var(name) {
        if !value.trim().is_empty() {
            *target = value;
        }
    }
}

fn override_option(name: &str, target: &mut Option<String>) {
    if let Ok(value) = env::var(name) {
        *target = if value.is_empty() { None } else { Some(value) };
    }
}

fn override_u16(name: &str, target: &mut u16) {
    if let Ok(value) = env::var(name) {
        if let Ok(parsed) = value.parse() {
            *target = parsed;
        }
    }
}

fn default_mqtt_port() -> u16 {
    1883
}
fn default_region() -> String {
    "us-east-1".into()
}
fn default_true() -> bool {
    true
}
fn default_retention_days() -> u32 {
    14
}
fn default_source_kind() -> String {
    "simulator".into()
}
fn default_sample_rate() -> u32 {
    2_000
}
fn default_window_seconds() -> f32 {
    10.0
}
fn default_publish_interval() -> u64 {
    15
}
fn default_anomaly_every() -> u64 {
    12
}
fn default_seed() -> u64 {
    42
}
fn default_baseline_rms() -> f32 {
    0.08
}
fn default_kurtosis_reference() -> f32 {
    3.0
}
fn default_alert_threshold() -> f32 {
    0.75
}
