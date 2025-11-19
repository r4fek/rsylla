"""
Tests for QueryResult and Row
"""
import pytest
from rscylla import Session


@pytest.mark.integration
class TestQueryResult:
    """Test QueryResult functionality"""

    async def test_result_rows(self, session, users_table, sample_users):
        """Test getting all rows"""
        result = await session.execute("SELECT * FROM users")
        rows = result.rows()

        assert rows is not None
        assert len(rows) == len(sample_users)

    async def test_result_first_row(self, session, users_table, sample_users):
        """Test getting first row"""
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()

        assert row is not None
        assert len(row) > 0

    async def test_result_first_row_empty(self, session, users_table):
        """Test first_row on empty result"""
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 9999})
        row = result.first_row()

        assert row is None

    async def test_result_single_row(self, session, users_table, sample_users):
        """Test getting single row"""
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
        row = result.single_row()

        assert row is not None

    async def test_result_single_row_error(self, session, users_table, sample_users):
        """Test single_row with multiple rows"""
        result = await session.execute("SELECT * FROM users")

        with pytest.raises(Exception):  # Should raise because multiple rows
            result.single_row()

    async def test_result_first_row_typed(self, session, users_table, sample_users):
        """Test getting first row as dict"""
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
        row_dict = result.first_row_typed()

        assert row_dict is not None
        assert isinstance(row_dict, dict)

    async def test_result_rows_typed(self, session, users_table, sample_users):
        """Test getting all rows as dicts"""
        result = await session.execute("SELECT * FROM users")
        rows_dicts = result.rows_typed()

        assert rows_dicts is not None
        assert isinstance(rows_dicts, list)
        assert len(rows_dicts) == len(sample_users)
        assert all(isinstance(row, dict) for row in rows_dicts)

    async def test_result_col_specs(self, session, users_table):
        """Test getting column specifications"""
        result = await session.execute("SELECT * FROM users")
        col_specs = result.col_specs()

        assert col_specs is not None
        assert isinstance(col_specs, list)
        assert len(col_specs) > 0

    async def test_result_warnings(self, session, users_table):
        """Test getting warnings"""
        result = await session.execute("SELECT * FROM users")
        warnings = result.warnings()

        assert warnings is not None
        assert isinstance(warnings, list)

    async def test_result_iteration(self, session, users_table, sample_users):
        """Test iterating over result"""
        result = await session.execute("SELECT * FROM users")

        count = 0
        for row in result:
            assert row is not None
            count += 1

        assert count == len(sample_users)

    async def test_result_len(self, session, users_table, sample_users):
        """Test result length"""
        result = await session.execute("SELECT * FROM users")
        length = len(result)

        assert length == len(sample_users)

    async def test_result_bool(self, session, users_table, sample_users):
        """Test result boolean check"""
        result = await session.execute("SELECT * FROM users")
        assert bool(result) is True

        result_empty = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 9999})
        assert bool(result_empty) is False


@pytest.mark.integration
class TestRow:
    """Test Row functionality"""

    async def test_row_columns(self, session, users_table, sample_users):
        """Test getting row columns"""
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()

        columns = row.columns()
        assert columns is not None
        assert isinstance(columns, list)
        assert len(columns) > 0

    async def test_row_get(self, session, users_table, sample_users):
        """Test getting column by index"""
        result = await session.execute("SELECT id, username FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()

        id_val = row.get(0)
        assert id_val == 1

        username = row.get(1)
        assert username == "alice"

    async def test_row_get_invalid_index(self, session, users_table, sample_users):
        """Test getting column with invalid index"""
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()

        with pytest.raises(Exception):
            row.get(999)

    async def test_row_indexing(self, session, users_table, sample_users):
        """Test row indexing"""
        result = await session.execute("SELECT id, username FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()

        assert row[0] == 1
        assert row[1] == "alice"

    async def test_row_negative_indexing(self, session, users_table, sample_users):
        """Test row negative indexing"""
        result = await session.execute("SELECT id, username FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()

        last_col = row[-1]
        assert last_col is not None

    async def test_row_len(self, session, users_table, sample_users):
        """Test row length"""
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()

        length = len(row)
        assert length > 0

    async def test_row_as_dict(self, session, users_table, sample_users):
        """Test converting row to dict"""
        result = await session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()

        row_dict = row.as_dict()
        assert row_dict is not None
        assert isinstance(row_dict, dict)
