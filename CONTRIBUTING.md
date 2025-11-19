# Contributing to rscylla

Thank you for your interest in contributing to rscylla! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Rust (latest stable) - Install from [rustup.rs](https://rustup.rs/)
- Python 3.8 or higher
- maturin - `pip install maturin`

### Building from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/rscylla.git
cd rscylla

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install maturin
pip install maturin

# Build and install in development mode
maturin develop
```

## Project Structure

```
rscylla/
├── src/                    # Rust source code
│   ├── lib.rs             # Main library entry point
│   ├── session.rs         # Session and SessionBuilder
│   ├── query.rs           # Query and PreparedStatement
│   ├── result.rs          # QueryResult and Row
│   ├── batch.rs           # Batch operations
│   ├── types.rs           # Type conversions
│   └── error.rs           # Error handling
├── python/rscylla/        # Python package
│   ├── __init__.py        # Python module initialization
│   └── __init__.pyi       # Type stubs
├── examples/              # Example scripts
├── Cargo.toml            # Rust dependencies
└── pyproject.toml        # Python packaging configuration
```

## Adding New Features

When adding bindings for new scylla-rust-driver features:

1. **Update Rust code**: Add the binding in the appropriate module (session.rs, query.rs, etc.)
2. **Update Python types**: Add type hints to `python/rscylla/__init__.pyi`
3. **Export in lib.rs**: Make sure the new class/function is registered in `lib.rs`
4. **Update __init__.py**: Add to exports in `python/rscylla/__init__.py`
5. **Add tests**: Create tests for the new functionality
6. **Update documentation**: Add usage examples to README.md
7. **Create example**: Add example script if the feature is substantial

## Code Style

### Rust Code

- Follow Rust standard formatting (use `cargo fmt`)
- Run `cargo clippy` and address warnings
- Add documentation comments for public APIs

### Python Code

- Follow PEP 8 style guide
- Use type hints
- Add docstrings for public functions

## Testing

```bash
# Run Rust tests
cargo test

# Test the Python package
maturin develop
python -m pytest tests/

# Run examples
python examples/basic_usage.py
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Pull Request Guidelines

- Describe what your PR does and why
- Reference any related issues
- Ensure all tests pass
- Update documentation as needed
- Keep commits focused and atomic
- Write clear commit messages

## Reporting Issues

When reporting issues, please include:

- Python version
- Rust version
- Operating system
- ScyllaDB/Cassandra version
- Minimal code to reproduce the issue
- Error messages and stack traces

## Questions?

Feel free to open an issue for any questions or concerns.

## License

By contributing to rscylla, you agree that your contributions will be licensed under both MIT and Apache-2.0 licenses.
