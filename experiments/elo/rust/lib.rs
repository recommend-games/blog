pub mod core;

use crate::core::rating_system::EloRatingSystem;
use crate::core::rating_system::{EloConfig, Match};
use crate::core::two_player::TwoPlayerElo;
use ndarray::ArrayView2;
use numpy::PyReadonlyArray2;
use once_cell::sync::Lazy;
use pyo3::prelude::*;
use std::collections::HashMap;

pub static PERMS: Lazy<Vec<Vec<Vec<usize>>>> = Lazy::new(|| {
    // PERMS[n] = all permutations of 0..n-1, for n up to 6
    let mut out: Vec<Vec<Vec<usize>>> = vec![vec![]; 7];
    for n in 0..=6 {
        let mut perms = Vec::new();
        let mut a: Vec<usize> = (0..n).collect();
        heap_permute(n, &mut a, &mut perms);
        out[n] = perms;
    }
    out
});

fn heap_permute(k: usize, a: &mut [usize], out: &mut Vec<Vec<usize>>) {
    if k <= 1 {
        out.push(a.to_vec());
        return;
    }
    heap_permute(k - 1, a, out);
    for i in 0..(k - 1) {
        if k % 2 == 0 {
            a.swap(i, k - 1);
        } else {
            a.swap(0, k - 1);
        }
        heap_permute(k - 1, a, out);
    }
}

fn hello_core() -> String {
    "Hello from example-ext!".to_string()
}

#[pyfunction]
fn hello_from_bin() -> String {
    hello_core()
}

pub fn hello_for_rust() -> String {
    hello_core()
}

#[pyfunction]
fn calculate_elo_ratings_rust<'py>(
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
        elo.update(Match::Ordered(row.to_vec()));
    }

    Ok(elo.ratings().clone())
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_from_bin, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_elo_ratings_rust, m)?)?;
    Ok(())
}
