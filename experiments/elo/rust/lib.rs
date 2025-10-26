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
    matches: PyReadonlyArray2<'py, i32>, // shape: (n_matches, n_players)
    two_player_only: bool,
    min_elo_k: f64,
    max_elo_k: f64,
    elo_scale: f64,
    max_iterations: Option<usize>,
    x_absolute_tol: Option<f64>,
) -> PyResult<f64> {
    let arr: ArrayView2<'_, i32> = matches.as_array();
    if arr.ndim() != 2 || arr.shape()[1] < 2 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "matches must be shape (n_matches, n_players>=2) of int32",
        ));
    }

    let matches = arr
        .rows()
        .into_iter()
        .map(|r| Match::Ordered(r.to_vec()))
        .collect::<Vec<Match<i32>>>();

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
