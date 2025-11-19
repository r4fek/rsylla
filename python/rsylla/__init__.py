"""
rsylla - Python bindings for ScyllaDB using scylla-rust-driver

This package provides high-performance Python bindings for ScyllaDB/Cassandra
using the official Rust driver.
"""

from ._rsylla import (
    Batch,
    PreparedStatement,
    Query,
    QueryResult,
    Row,
    ScyllaError,
    Session,
    SessionBuilder,
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
