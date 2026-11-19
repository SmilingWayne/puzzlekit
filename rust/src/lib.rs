use cspuz_solver_backend::{decode_and_solve, list_puzzles_for_solve, Uniqueness};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;

/// Solve a supported URL and return the upstream board plus answer status.
#[pyfunction]
fn solve_url(py: Python<'_>, url: String) -> PyResult<(String, &'static str)> {
    let result = py.detach(|| std::panic::catch_unwind(|| decode_and_solve(url.as_bytes())))
        .map_err(|_| PyRuntimeError::new_err("cspuz failed while processing the puzzle"))?
        .map_err(PyValueError::new_err)?;
    let status = match result.uniqueness {
        Uniqueness::Unique => "unique",
        Uniqueness::NonUnique => "multiple",
        Uniqueness::NoAnswer => "no_solution",
        Uniqueness::NotApplicable => "unknown",
    };
    Ok((result.to_json(), status))
}

#[pyfunction]
fn supported_puzzles() -> Vec<(String, String)> {
    list_puzzles_for_solve()
}

#[pymodule]
fn _cspuz(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve_url, m)?)?;
    m.add_function(wrap_pyfunction!(supported_puzzles, m)?)?;
    Ok(())
}
