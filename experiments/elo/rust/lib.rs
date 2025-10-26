pub mod core;

use crate::core::multi_player::RankOrderedLogitElo;
use crate::core::optimal_k::approx_optimal_k;
use crate::core::rating_system::EloRatingSystem;
use crate::core::rating_system::{EloConfig, Match};
use crate::core::two_player::TwoPlayerElo;
use ndarray::ArrayView2;
use numpy::PyReadonlyArray2;
use pyo3::prelude::*;
use std::collections::HashMap;

#[pyfunction]
fn approx_optimal_k_rust<'py>(
    players: numpy::PyReadonlyArray1<'py, i64>,
    payoffs: Option<numpy::PyReadonlyArray1<'py, f64>>,
    row_splits: numpy::PyReadonlyArray1<'py, i64>,
    two_player_only: bool,
    min_elo_k: f64,
    max_elo_k: f64,
    elo_scale: f64,
    max_iterations: Option<usize>,
    x_absolute_tol: Option<f64>,
) -> PyResult<f64> {
    let p = players.as_slice()?;
    let rs = row_splits.as_slice()?;

    if rs.len() < 2 || rs[0] != 0 || *rs.last().unwrap() as usize != p.len() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "row_splits must start at 0 and end at players.len()",
        ));
    }

    let matches: Vec<Match<i64>> = if let Some(payoffs) = payoffs {
        let payoffs = payoffs.as_slice()?;
        if payoffs.len() != p.len() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "payoffs length must equal players length",
            ));
        }
        rs.windows(2)
            .map(|w| {
                Match::Outcomes(
                    p[w[0] as usize..w[1] as usize]
                        .iter()
                        .cloned()
                        .zip(payoffs[w[0] as usize..w[1] as usize].iter().cloned())
                        .collect(),
                )
            })
            .collect::<Vec<_>>()
    } else {
        rs.windows(2)
            .map(|w| Match::Ordered(p[w[0] as usize..w[1] as usize].to_vec()))
            .collect::<Vec<_>>()
    };

    let optimal_k = approx_optimal_k(
        &matches,
        two_player_only,
        min_elo_k,
        max_elo_k,
        elo_scale,
        max_iterations,
        x_absolute_tol,
    );

    Ok(optimal_k)
}

#[pyfunction]
fn calculate_elo_ratings_two_players_rust<'py>(
    matches: PyReadonlyArray2<'py, i32>, // shape: (n_matches, 2)
    elo_initial: f64,
    elo_k: f64,
    elo_scale: f64,
) -> PyResult<HashMap<i32, f64>> {
    // Simple, straightforward implementation (winner, loser pairs).
    let arr: ArrayView2<'_, i32> = matches.as_array();
    if arr.ndim() != 2 || arr.shape()[1] != 2 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "matches must be shape (n_matches, 2) of int32",
        ));
    }
    let cfg = EloConfig {
        elo_initial,
        elo_k,
        elo_scale,
    };
    let mut elo = TwoPlayerElo::<i32>::new(cfg, None);

    for row in arr.rows() {
        elo.update_elo_ratings(Match::Ordered(row.to_vec()));
    }

    Ok(elo.ratings().clone())
}

#[pyfunction]
fn calculate_elo_ratings_multi_players_rust<'py>(
    matches: PyReadonlyArray2<'py, i32>, // shape: (n_matches, n_players)
    elo_initial: f64,
    elo_k: f64,
    elo_scale: f64,
) -> PyResult<HashMap<i32, f64>> {
    // Simple, straightforward implementation (ordered players).
    let arr: ArrayView2<'_, i32> = matches.as_array();
    if arr.ndim() != 2 || arr.shape()[1] < 2 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "matches must be shape (n_matches, n_players>=2) of int32",
        ));
    }
    let cfg = EloConfig {
        elo_initial,
        elo_k,
        elo_scale,
    };
    let mut elo = RankOrderedLogitElo::<i32>::new(cfg, None, 6, 12);

    for row in arr.rows() {
        elo.update_elo_ratings(Match::Ordered(row.to_vec()));
    }

    Ok(elo.ratings().clone())
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(approx_optimal_k_rust, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_elo_ratings_two_players_rust, m)?)?;
    m.add_function(wrap_pyfunction!(
        calculate_elo_ratings_multi_players_rust,
        m
    )?)?;
    Ok(())
}
