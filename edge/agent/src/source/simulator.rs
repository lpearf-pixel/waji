use crate::{
    config::SourceConfig,
    model::{VibrationSample, VibrationWindow},
    source::VibrationSource,
};
use anyhow::Result;
use chrono::Utc;
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;
use rand_distr::{Distribution, Normal};

pub struct SimulatorSource {
    config: SourceConfig,
    rng: ChaCha8Rng,
    window_index: u64,
    noise: Normal<f32>,
}

impl SimulatorSource {
    pub fn new(config: SourceConfig) -> Self {
        Self {
            rng: ChaCha8Rng::seed_from_u64(config.seed),
            config,
            window_index: 0,
            noise: Normal::new(0.0, 0.004).expect("valid simulator noise"),
        }
    }

    fn generate_window(&mut self) -> VibrationWindow {
        self.window_index += 1;
        let sample_count =
            (self.config.sample_rate_hz as f32 * self.config.window_seconds).round() as usize;
        let anomaly = self.config.anomaly_every_windows > 0
            && self.window_index % self.config.anomaly_every_windows == 0;
        let sample_rate = self.config.sample_rate_hz as f32;
        let mut samples = Vec::with_capacity(sample_count);

        for index in 0..sample_count {
            let time = index as f32 / sample_rate;
            let shaft = (2.0 * std::f32::consts::PI * 30.0 * time).sin();
            let pump = (2.0 * std::f32::consts::PI * 120.0 * time).sin();
            let high = (2.0 * std::f32::consts::PI * 280.0 * time).sin();
            let impulse = if anomaly
                && index % (self.config.sample_rate_hz as usize / 4).max(1) < 3
            {
                self.rng.gen_range(0.25..0.45)
            } else {
                0.0
            };
            let anomaly_component = if anomaly {
                0.12 * high + impulse
            } else {
                0.0
            };

            samples.push(VibrationSample {
                x_g: 0.055 * shaft
                    + 0.015 * pump
                    + anomaly_component
                    + self.noise.sample(&mut self.rng),
                y_g: 0.040 * shaft
                    + 0.020 * pump
                    + 0.65 * anomaly_component
                    + self.noise.sample(&mut self.rng),
                z_g: 1.0
                    + 0.030 * shaft
                    + 0.012 * pump
                    + 0.45 * anomaly_component
                    + self.noise.sample(&mut self.rng),
            });
        }

        VibrationWindow {
            started_at: Utc::now(),
            sample_rate_hz: self.config.sample_rate_hz,
            samples,
            simulated_fault: anomaly,
        }
    }
}

impl VibrationSource for SimulatorSource {
    fn next_window(&mut self) -> Result<VibrationWindow> {
        Ok(self.generate_window())
    }
}
