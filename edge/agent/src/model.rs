use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct VibrationSample {
    pub x_g: f32,
    pub y_g: f32,
    pub z_g: f32,
}

#[derive(Debug, Clone)]
pub struct VibrationWindow {
    pub started_at: DateTime<Utc>,
    pub sample_rate_hz: u32,
    pub samples: Vec<VibrationSample>,
    pub simulated_fault: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AxisFeatures {
    pub mean_g: f32,
    pub rms_g: f32,
    pub std_dev_g: f32,
    pub peak_abs_g: f32,
    pub peak_to_peak_g: f32,
    pub kurtosis: f32,
    pub crest_factor: f32,
    pub dominant_frequency_hz: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VibrationFeatures {
    pub algorithm: String,
    pub x: AxisFeatures,
    pub y: AxisFeatures,
    pub z: AxisFeatures,
    pub vector_rms_g: f32,
    pub anomaly_score: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BatchMetadata {
    pub schema_version: String,
    pub batch_id: String,
    pub device_id: String,
    pub machine_type: String,
    pub machine_model: String,
    pub sensor_id: String,
    pub sensor_position: String,
    pub sensor_orientation: String,
    pub source_kind: String,
    pub started_at: DateTime<Utc>,
    pub duration_seconds: f32,
    pub sample_rate_hz: u32,
    pub sample_count: usize,
    pub data_object_key: String,
    pub metadata_object_key: String,
    pub data_sha256: String,
    pub simulated_fault: bool,
    pub features: VibrationFeatures,
}

#[derive(Debug, Serialize)]
pub struct DeviceStatus<'a> {
    pub device_id: &'a str,
    pub status: &'a str,
    pub agent_version: &'a str,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize)]
pub struct UploadEvent<'a> {
    pub batch_id: &'a str,
    pub data_object_key: &'a str,
    pub metadata_object_key: &'a str,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize)]
pub struct AlertEvent<'a> {
    pub batch_id: &'a str,
    pub sensor_id: &'a str,
    pub sensor_position: &'a str,
    pub anomaly_score: f32,
    pub algorithm: &'a str,
    pub timestamp: DateTime<Utc>,
}
