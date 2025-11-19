"""
rscylla - Python bindings for ScyllaDB using scylla-rust-driver

This package provides high-performance Python bindings for ScyllaDB/Cassandra
using the official Rust driver.
"""

from ._rscylla import (
    Session,
    SessionBuilder,
    Query,
    PreparedStatement,
    QueryResult,
    Row,
    Batch,
    ScyllaError,
)

__version__ = "0.1.0"

__all__ = [
    "Session",
    "SessionBuilder",
    "Query",
    "PreparedStatement",
    "QueryResult",
    "Row",
    "Batch",
    "ScyllaError",
]
