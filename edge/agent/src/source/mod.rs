mod simulator;

use crate::model::VibrationWindow;
use anyhow::Result;

pub use simulator::SimulatorSource;

pub trait VibrationSource {
    fn next_window(&mut self) -> Result<VibrationWindow>;
}
