// src/optimal_k.rs (or wherever you keep helpers)
use std::collections::HashMap;
use std::hash::Hash;

use crate::core::multi_player::RankOrderedLogitElo;
use crate::core::rating_system::{EloConfig, EloRatingSystem, Match};
use crate::core::two_player::TwoPlayerElo;
use argmin::core::{CostFunction, Error, Executor, State};
use argmin::solver::brent::BrentOpt;

/// Compute mean squared error of the per-player diffs produced over a batch.
/// Diffs are the normalised (observed - expected) values returned by the rating updates.
fn calculate_loss<Id>(elo: &mut dyn EloRatingSystem<Id>, matches: &[Match<Id>]) -> f64
where
    Id: Eq + Hash + Clone,
{
    let Some(all_diffs) = elo.update_elo_ratings_batch_slice(matches, true) else {
        return f64::INFINITY;
    };

    let mut sum_match_mse = 0.0f64;
    let mut num_matches = 0usize;

    for diffs in all_diffs {
        let mut sum_sq = 0.0f64;
        let mut count = 0usize;
        for d in diffs {
            if d.is_finite() {
                sum_sq += d * d;
                count += 1;
            }
        }
        if count > 0 {
            sum_match_mse += sum_sq / (count as f64);
            num_matches += 1;
        }
    }

    if num_matches == 0 {
        f64::INFINITY
    } else {
        sum_match_mse / (num_matches as f64)
    }
}

/// Argmin problem: minimise the Elo diff MSE over k in [min_k, max_k].
struct BrentKProblem<'a, Id> {
    matches: &'a [Match<Id>],
    elo_scale: f64,
    two_player_only: bool,
}

impl<'a, Id> CostFunction for BrentKProblem<'a, Id>
where
    Id: Eq + Hash + Clone,
{
    type Param = f64;
    type Output = f64;

    fn cost(&self, k: &Self::Param) -> Result<Self::Output, Error> {
        // Guard against degenerate inputs
        if !k.is_finite() || *k < 0.0 {
            return Ok(f64::INFINITY);
        }
        let mut sys: Box<dyn EloRatingSystem<Id>> = if self.two_player_only {
            Box::new(TwoPlayerElo::new(
                EloConfig {
                    elo_k: *k,
                    elo_scale: self.elo_scale,
                    ..EloConfig::default()
                },
                Some(HashMap::new()),
            ))
        } else {
            Box::new(RankOrderedLogitElo::new(
                EloConfig {
                    elo_k: *k,
                    elo_scale: self.elo_scale,
                    ..EloConfig::default()
                },
                Some(HashMap::new()),
                6,
                12,
            ))
        };
        Ok(calculate_loss::<Id>(sys.as_mut(), self.matches))
    }
}

/// Port of Python's `approximate_optimal_k(..., two_player_only=True, ...)`.
/// Minimises the MSE of diffs over k in [min_k, max_k].
pub fn approx_optimal_k<Id>(
    matches: &[Match<Id>],
    two_player_only: bool,
    min_k: f64,
    max_k: f64,
    elo_scale: f64,                // default 400.0 in EloConfig::default()
    max_iterations: Option<usize>, // Python's `maxiter`
    x_absolute_tol: Option<f64>,   // Python's `xatol`
) -> f64
where
    Id: Eq + Hash + Clone,
{
    let max_iters = max_iterations.unwrap_or(200) as u64;

    // Brent uses combined tolerance: tol = eps * |x| + t.
    // We map the provided absolute tolerance to `t` and keep default `eps = sqrt(machine_epsilon)`.
    let abs_tol = x_absolute_tol.unwrap_or(1e-3);
    let eps = f64::EPSILON.sqrt();

    let problem = BrentKProblem {
        matches,
        elo_scale,
        two_player_only,
    };

    let solver = BrentOpt::new(min_k, max_k).set_tolerance(eps, abs_tol);

    // Use the mid-point as an initial guess for completeness (Brent brackets anyway).
    let init = 0.5 * (min_k + max_k);

    let res = Executor::new(problem, solver)
        .configure(|state| state.param(init).max_iters(max_iters))
        .run();

    match res {
        Ok(res) => {
            // Prefer the best parameter found; fall back to the last one if unset.
            if let Some(k) = res.state().get_best_param() {
                *k
            } else if let Some(k) = res.state().get_param() {
                *k
            } else {
                // Shouldn't happen; conservative fallback.
                init
            }
        }
        Err(_e) => {
            // On failure, return the mid-point as a safe fallback.
            init
        }
    }
}
