// src/optimal_k.rs (or wherever you keep helpers)
use std::collections::HashMap;
use std::hash::Hash;

use crate::core::rating_system::{EloConfig, EloRatingSystem, Match};
use crate::core::two_player::TwoPlayerElo;

/// Compute mean squared error of the per-player diffs produced over a batch.
/// Diffs are the normalised (observed - expected) values returned by the rating updates.
fn calculate_loss<Id, S>(elo: &mut S, matches: &[Match<Id>]) -> f64
where
    Id: Eq + Hash + Clone,
    S: EloRatingSystem<Id>,
{
    let Some(all_diffs) = elo.update_elo_ratings_batch(matches.iter().cloned(), true) else {
        return f64::INFINITY;
    };

    let mut sum = 0.0f64;
    let mut n = 0usize;
    for diffs in all_diffs {
        for d in diffs {
            if d.is_finite() {
                sum += d * d;
                n += 1;
            }
        }
    }
    if n == 0 {
        f64::INFINITY
    } else {
        sum / (n as f64)
    }
}

/// Simple golden-section search for bounded scalar minimisation.
/// Returns the x that (approximately) minimises f on [a, b].
fn golden_section_search<F>(mut a: f64, mut b: f64, tol: f64, max_iters: usize, f: F) -> f64
where
    F: Fn(f64) -> f64,
{
    // φ = (1 + sqrt(5)) / 2; 1 - 1/φ = 1/φ^2 ≈ 0.381966...
    let gr = 0.5 * (5.0_f64.sqrt() + 1.0);
    let inv_gr2 = 1.0 / (gr * gr);

    let mut c = b - (b - a) * inv_gr2;
    let mut d = a + (b - a) * inv_gr2;
    let mut fc = f(c);
    let mut fd = f(d);

    for _ in 0..max_iters {
        if (b - a).abs() <= tol {
            break;
        }
        if fc < fd {
            b = d;
            d = c;
            fd = fc;
            c = b - (b - a) * inv_gr2;
            fc = f(c);
        } else {
            a = c;
            c = d;
            fc = fd;
            d = a + (b - a) * inv_gr2;
            fd = f(d);
        }
    }
    // Return the best of c/d region
    if fc < fd {
        c
    } else {
        d
    }
}

/// Port of Python's `approximate_optimal_k(..., two_player_only=True, ...)`.
/// Minimises the MSE of diffs over k in [min_k, max_k].
pub fn approx_optimal_k_two_player<Id>(
    matches: &[Match<Id>],
    min_k: f64,
    max_k: f64,
    elo_scale: f64,                // default 400.0 in EloConfig::default()
    max_iterations: Option<usize>, // Python's `maxiter`
    x_absolute_tol: Option<f64>,   // Python's `xatol`
) -> f64
where
    Id: Eq + Hash + Clone,
{
    let max_iters = max_iterations.unwrap_or(200);
    let tol = x_absolute_tol.unwrap_or(1e-3);

    // Loss as a function of k: create a fresh system each time (like Python).
    let loss = |k: f64| -> f64 {
        // Guard against degenerate inputs
        if !k.is_finite() || k < 0.0 {
            return f64::INFINITY;
        }
        let mut sys: TwoPlayerElo<Id> = TwoPlayerElo::new(
            EloConfig {
                elo_k: k,
                elo_scale,
                ..EloConfig::default()
            },
            Some(HashMap::new()),
        );
        calculate_loss(&mut sys, matches)
    };

    golden_section_search(min_k, max_k, tol, max_iters, loss)
}
