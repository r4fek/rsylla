"""
Tests for Query execution
"""

import time

import pytest

from rscylla import Query, ScyllaError


@pytest.mark.integration
class TestQueryExecution:
    """Test query execution"""

    async def test_simple_query(self, session, test_keyspace):
        """Test simple SELECT query"""
        result = await session.execute("SELECT * FROM system.local")
        assert result is not None
        assert len(result) > 0

    async def test_create_table(self, session, test_keyspace):
        """Test CREATE TABLE"""
        await session.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id int PRIMARY KEY,
                name text
            )
        """
        )

        # Insert and query
        await session.execute(
            "INSERT INTO test_table (id, name) VALUES (?, ?)", {"id": 1, "name": "test"}
        )
        result = await session.execute("SELECT * FROM test_table WHERE id = ?", {"id": 1})

        assert len(result) == 1
        row = result.first_row()
        assert row is not None

        # Cleanup
        await session.execute("DROP TABLE IF EXISTS test_table")

    async def test_insert_and_select(self, session, users_table):
        """Test INSERT and SELECT"""
        # Insert
        await session.execute(
            "INSERT INTO users (id, username, email) VALUES (?, ?, ?)",
            {"id": 100, "username": "testuser", "email": "test@example.com"},
        )

        # Select
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 100})
        assert len(result) == 1

        row = result.first_row()
        assert row is not None

    async def test_update(self, session, users_table, sample_users):
        """Test UPDATE"""
        # Update
        await session.execute(
            "UPDATE users SET email = ? WHERE id = ?", {"email": "newemail@example.com", "id": 1}
        )

        # Verify
        result = await session.execute("SELECT email FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()
        email = row[0]
        assert email == "newemail@example.com"

    async def test_delete(self, session, users_table, sample_users):
        """Test DELETE"""
        # Delete
        await session.execute("DELETE FROM users WHERE id = ?", {"id": 1})

        # Verify
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
        assert len(result) == 0

    async def test_invalid_query(self, session, test_keyspace):
        """Test invalid query raises error"""
        with pytest.raises(ScyllaError):
            await session.execute("INVALID QUERY SYNTAX")


@pytest.mark.integration
class TestQueryObject:
    """Test Query class"""

    async def test_query_with_consistency(self, session, users_table, sample_users):
        """Test Query with consistency level"""
        query = Query("SELECT * FROM users WHERE id = ?").with_consistency("ONE")

        result = await session.query(query, {"id": 1})
        assert len(result) == 1

    async def test_query_with_page_size(self, session, users_table, sample_users):
        """Test Query with page size"""
        query = Query("SELECT * FROM users").with_page_size(2)

        result = await session.query(query)
        assert len(result) >= 2

    async def test_query_with_timeout(self, session, users_table):
        """Test Query with timeout"""
        query = Query("SELECT * FROM users").with_timeout(5000)

        result = await session.query(query)
        assert result is not None

    async def test_query_with_tracing(self, session, users_table, sample_users):
        """Test Query with tracing"""
        query = Query("SELECT * FROM users WHERE id = ?").with_tracing(True)

        result = await session.query(query, {"id": 1})
        assert result is not None

        # Check for trace ID
        _ = result.tracing_id()
        # Trace ID might be None in some cases, but the query should work

    async def test_query_with_timestamp(self, session, users_table):
        """Test Query with custom timestamp"""
        timestamp = int(time.time() * 1000000)

        query = Query("INSERT INTO users (id, username, email) VALUES (?, ?, ?)").with_timestamp(
            timestamp
        )

        await session.query(
            query, {"id": 200, "username": "timestampuser", "email": "ts@example.com"}
        )

        # Verify insert
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 200})
        assert len(result) == 1

    async def test_query_idempotency(self, session, users_table):
        """Test Query idempotency setting"""
        query = Query("SELECT * FROM users")

        # Initially should return some value
        _ = query.is_idempotent()

        # Set idempotent
        query.set_idempotent(True)
        assert query.is_idempotent() is True

        query.set_idempotent(False)
        assert query.is_idempotent() is False

    async def test_query_get_contents(self, session):
        """Test getting query contents"""
        query_str = "SELECT * FROM users"
        query = Query(query_str)

        contents = query.get_contents()
        assert contents == query_str

    async def test_query_all_consistency_levels(self, session, users_table):
        """Test all consistency levels"""
        # Only test consistency levels that work with a single-node cluster
        consistency_levels = ["ONE", "QUORUM", "ALL", "LOCAL_QUORUM", "LOCAL_ONE"]

        for consistency in consistency_levels:
            query = Query("SELECT * FROM users").with_consistency(consistency)
            # Should not raise error
            result = await session.query(query)
            assert result is not None
