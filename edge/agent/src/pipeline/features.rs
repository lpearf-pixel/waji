use crate::{
    config::PipelineConfig,
    model::{AxisFeatures, VibrationFeatures, VibrationSample},
};
use rustfft::{num_complex::Complex, FftPlanner};

pub fn compute_features(
    samples: &[VibrationSample],
    sample_rate_hz: u32,
    config: &PipelineConfig,
) -> VibrationFeatures {
    let x: Vec<f32> = samples.iter().map(|sample| sample.x_g).collect();
    let y: Vec<f32> = samples.iter().map(|sample| sample.y_g).collect();
    let z: Vec<f32> = samples.iter().map(|sample| sample.z_g).collect();

    let x_features = axis_features(&x, sample_rate_hz);
    let y_features = axis_features(&y, sample_rate_hz);
    let z_features = axis_features(&z, sample_rate_hz);
    let vector_rms_g = (x_features.rms_g.powi(2)
        + y_features.rms_g.powi(2)
        + z_features.rms_g.powi(2))
    .sqrt();

    let max_kurtosis = x_features
        .kurtosis
        .max(y_features.kurtosis)
        .max(z_features.kurtosis);
    let max_crest = x_features
        .crest_factor
        .max(y_features.crest_factor)
        .max(z_features.crest_factor);
    let rms_ratio = vector_rms_g / config.baseline_rms_g.max(0.000_001);
    let kurtosis_excess = (max_kurtosis - config.kurtosis_reference).max(0.0);
    let crest_excess = (max_crest - 3.0).max(0.0);
    let evidence = 0.55 * (rms_ratio - 1.0).max(0.0)
        + 0.30 * kurtosis_excess
        + 0.15 * crest_excess;
    let anomaly_score = (1.0 - (-evidence).exp()).clamp(0.0, 1.0);

    VibrationFeatures {
        algorithm: "heuristic_v1".into(),
        x: x_features,
        y: y_features,
        z: z_features,
        vector_rms_g,
        anomaly_score,
    }
}

fn axis_features(values: &[f32], sample_rate_hz: u32) -> AxisFeatures {
    if values.is_empty() {
        return AxisFeatures {
            mean_g: 0.0,
            rms_g: 0.0,
            std_dev_g: 0.0,
            peak_abs_g: 0.0,
            peak_to_peak_g: 0.0,
            kurtosis: 0.0,
            crest_factor: 0.0,
            dominant_frequency_hz: 0.0,
        };
    }

    let count = values.len() as f32;
    let mean = values.iter().sum::<f32>() / count;
    let centered: Vec<f32> = values.iter().map(|value| *value - mean).collect();
    let variance = centered.iter().map(|value| value * value).sum::<f32>() / count;
    let rms = variance.sqrt();
    let peak_abs = centered
        .iter()
        .map(|value| value.abs())
        .fold(0.0_f32, f32::max);
    let min = centered.iter().copied().fold(f32::INFINITY, f32::min);
    let max = centered
        .iter()
        .copied()
        .fold(f32::NEG_INFINITY, f32::max);
    let fourth_moment = centered.iter().map(|value| value.powi(4)).sum::<f32>() / count;
    let kurtosis = if variance > f32::EPSILON {
        fourth_moment / variance.powi(2)
    } else {
        0.0
    };
    let crest_factor = if rms > f32::EPSILON {
        peak_abs / rms
    } else {
        0.0
    };

    AxisFeatures {
        mean_g: mean,
        rms_g: rms,
        std_dev_g: rms,
        peak_abs_g: peak_abs,
        peak_to_peak_g: max - min,
        kurtosis,
        crest_factor,
        dominant_frequency_hz: dominant_frequency(&centered, sample_rate_hz),
    }
}

fn dominant_frequency(values: &[f32], sample_rate_hz: u32) -> f32 {
    if values.len() < 2 {
        return 0.0;
    }

    let mut planner = FftPlanner::<f32>::new();
    let fft = planner.plan_fft_forward(values.len());
    let mut buffer: Vec<Complex<f32>> = values
        .iter()
        .map(|value| Complex::new(*value, 0.0))
        .collect();
    fft.process(&mut buffer);

    let half = buffer.len() / 2;
    let (index, _) = buffer
        .iter()
        .take(half)
        .enumerate()
        .skip(1)
        .map(|(index, value)| (index, value.norm_sqr()))
        .max_by(|left, right| left.1.total_cmp(&right.1))
        .unwrap_or((0, 0.0));

    index as f32 * sample_rate_hz as f32 / values.len() as f32
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finds_dominant_frequency() {
        let sample_rate = 1_000;
        let samples: Vec<VibrationSample> = (0..1_000)
            .map(|index| {
                let value = (2.0
                    * std::f32::consts::PI
                    * 50.0
                    * index as f32
                    / sample_rate as f32)
                    .sin();
                VibrationSample {
                    x_g: value,
                    y_g: 0.0,
                    z_g: 1.0,
                }
            })
            .collect();
        let features = compute_features(&samples, sample_rate, &PipelineConfig::default());
        assert!((features.x.dominant_frequency_hz - 50.0).abs() < 1.0);
    }
}
