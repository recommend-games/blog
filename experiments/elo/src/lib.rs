use once_cell::sync::Lazy;
use pyo3::prelude::*;

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

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_from_bin, m)?)?;
    Ok(())
}
