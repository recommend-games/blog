use pyo3::prelude::*;

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
