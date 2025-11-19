use pyo3::prelude::*;
use pyo3::create_exception;

create_exception!(rscylla, ScyllaError, pyo3::exceptions::PyException);

// Helper functions to convert scylla errors to PyErr
// We can't implement From directly due to orphan rules
pub fn query_error_to_py(err: scylla::transport::errors::QueryError) -> PyErr {
    PyErr::new::<ScyllaError, _>(format!("Query error: {}", err))
}

pub fn session_error_to_py(err: scylla::transport::errors::NewSessionError) -> PyErr {
    PyErr::new::<ScyllaError, _>(format!("Session error: {}", err))
}

pub fn serialization_error_to_py(err: scylla::serialize::SerializationError) -> PyErr {
    PyErr::new::<ScyllaError, _>(format!("Serialization error: {}", err))
}

pub fn deserialization_error_to_py(err: scylla::deserialize::DeserializationError) -> PyErr {
    PyErr::new::<ScyllaError, _>(format!("Deserialization error: {}", err))
}
