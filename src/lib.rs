use pyo3::prelude::*;

mod error;
mod session;
mod query;
mod result;
mod batch;
mod types;

use error::ScyllaError;
use session::{Session, SessionBuilder};
use query::{Query, PreparedStatement};
use result::{QueryResult, Row};
use batch::Batch;

#[pymodule]
fn _rscylla(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Core types
    m.add_class::<SessionBuilder>()?;
    m.add_class::<Session>()?;
    m.add_class::<Query>()?;
    m.add_class::<PreparedStatement>()?;
    m.add_class::<QueryResult>()?;
    m.add_class::<Row>()?;
    m.add_class::<Batch>()?;

    // Exception
    m.add("ScyllaError", _py.get_type_bound::<ScyllaError>())?;

    Ok(())
}
