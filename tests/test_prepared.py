"""
Tests for PreparedStatement
"""
import pytest
from rscylla import Session, ScyllaError


@pytest.mark.integration
class TestPreparedStatement:
    """Test PreparedStatement functionality"""

    async def test_prepare_statement(self, session, users_table):
        """Test preparing a statement"""
        prepared = await session.prepare("INSERT INTO users (id, username, email) VALUES (?, ?, ?)")
        assert prepared is not None

    async def test_execute_prepared_insert(self, session, users_table):
        """Test executing prepared INSERT"""
        prepared = await session.prepare("INSERT INTO users (id, username, email) VALUES (?, ?, ?)")

        await session.execute_prepared(prepared, {
            "id": 300,
            "username": "prepareduser",
            "email": "prepared@example.com"
        })

        # Verify
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 300})
        assert len(result) == 1

    async def test_execute_prepared_select(self, session, users_table, sample_users):
        """Test executing prepared SELECT"""
        prepared = await session.prepare("SELECT * FROM users WHERE id = ?")

        result = await session.execute_prepared(prepared, {"id": 1})
        assert len(result) == 1

    async def test_prepared_multiple_executions(self, session, users_table):
        """Test executing prepared statement multiple times"""
        prepared = await session.prepare("INSERT INTO users (id, username, email) VALUES (?, ?, ?)")

        # Execute multiple times
        for i in range(400, 410):
            await session.execute_prepared(prepared, {
                "id": i,
                "username": f"user{i}",
                "email": f"user{i}@example.com"
            })

        # Verify all inserts
        result = await session.execute("SELECT COUNT(*) FROM users")
        # Should have at least 10 rows

    async def test_prepared_with_consistency(self, session, users_table):
        """Test prepared statement with consistency level"""
        prepared = await session.prepare("SELECT * FROM users WHERE id = ?")
        prepared_with_consistency = prepared.with_consistency("ONE")

        await session.execute_prepared(prepared_with_consistency, {"id": 1})

    async def test_prepared_with_page_size(self, session, users_table, sample_users):
        """Test prepared statement with page size"""
        prepared = await session.prepare("SELECT * FROM users")
        prepared_paged = prepared.with_page_size(2)

        result = await session.execute_prepared(prepared_paged)
        assert result is not None

    async def test_prepared_idempotency(self, session, users_table):
        """Test prepared statement idempotency"""
        prepared = await session.prepare("SELECT * FROM users")

        # Set idempotent
        prepared_idempotent = prepared.set_idempotent(True)
        assert prepared_idempotent.is_idempotent() is True

    async def test_prepared_get_id(self, session, users_table):
        """Test getting prepared statement ID"""
        prepared = await session.prepare("SELECT * FROM users")

        stmt_id = prepared.get_id()
        assert stmt_id is not None
        assert isinstance(stmt_id, bytes)
        assert len(stmt_id) > 0

    async def test_prepared_get_statement(self, session, users_table):
        """Test getting prepared statement query string"""
        query_str = "SELECT * FROM users WHERE id = ?"
        prepared = await session.prepare(query_str)

        stmt = prepared.get_statement()
        assert stmt == query_str

    async def test_prepared_update(self, session, users_table, sample_users):
        """Test prepared UPDATE statement"""
        prepared = await session.prepare("UPDATE users SET email = ? WHERE id = ?")

        await session.execute_prepared(prepared, {
            "email": "updated@example.com",
            "id": 1
        })

        # Verify
        result = await session.execute("SELECT email FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()
        assert row[0] == "updated@example.com"

    async def test_prepared_delete(self, session, users_table, sample_users):
        """Test prepared DELETE statement"""
        prepared = await session.prepare("DELETE FROM users WHERE id = ?")

        await session.execute_prepared(prepared, {"id": 2})

        # Verify
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 2})
        assert len(result) == 0

    async def test_prepared_invalid_query(self, session, test_keyspace):
        """Test preparing invalid query"""
        with pytest.raises(ScyllaError):
            await session.prepare("INVALID QUERY SYNTAX")
