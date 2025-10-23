pub mod rating_system;
// pub mod two_player;

/// Elo win probability for player A vs B given rating difference `diff = r_a - r_b`.
#[inline]
pub fn elo_probability(diff: f64, scale: f64) -> f64 {
    // 1 / (1 + 10^(-diff/scale))
    1.0 / (1.0 + 10f64.powf(-diff / scale))
}
