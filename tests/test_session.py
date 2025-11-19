"""
Tests for Session and SessionBuilder
"""

import pytest

from rscylla import ScyllaError, Session, SessionBuilder


@pytest.mark.integration
class TestSessionBuilder:
    """Test SessionBuilder configuration"""

    async def test_simple_connection(self, scylla_connection_string):
        """Test simple session creation"""
        session = await Session.connect([scylla_connection_string])
        assert session is not None

        # Test with a simple query
        result = await session.execute("SELECT now() FROM system.local")
        assert result is not None

    async def test_session_builder_basic(self, scylla_connection_string):
        """Test SessionBuilder basic configuration"""
        session = await SessionBuilder().known_node(scylla_connection_string).build()
        assert session is not None

    async def test_session_builder_multiple_nodes(self, scylla_connection_string):
        """Test SessionBuilder with multiple nodes"""
        session = await SessionBuilder().known_nodes([scylla_connection_string]).build()
        assert session is not None

    async def test_session_builder_with_options(self, scylla_connection_string):
        """Test SessionBuilder with various options"""
        session = await (
            SessionBuilder()
            .known_node(scylla_connection_string)
            .connection_timeout(10000)
            .pool_size(10)
            .tcp_nodelay(True)
            .build()
        )
        assert session is not None

    async def test_session_builder_compression(self, scylla_connection_string):
        """Test SessionBuilder with compression"""
        # Test LZ4
        session_lz4 = await (
            SessionBuilder().known_node(scylla_connection_string).compression("lz4").build()
        )
        assert session_lz4 is not None

        # Test Snappy
        session_snappy = await (
            SessionBuilder().known_node(scylla_connection_string).compression("snappy").build()
        )
        assert session_snappy is not None

        # Test None
        session_none = await (
            SessionBuilder().known_node(scylla_connection_string).compression(None).build()
        )
        assert session_none is not None


@pytest.mark.integration
class TestSession:
    """Test Session methods"""

    async def test_use_keyspace(self, session, test_keyspace):
        """Test keyspace operations"""
        # Already using test_keyspace from fixture
        current = session.get_keyspace()
        assert current == test_keyspace

        # Change to system keyspace
        await session.use_keyspace("system", False)
        assert session.get_keyspace() == "system"

        # Change back
        await session.use_keyspace(test_keyspace, False)
        assert session.get_keyspace() == test_keyspace

    async def test_await_schema_agreement(self, session, test_keyspace):
        """Test schema agreement"""
        await session.execute(
            """
            CREATE TABLE IF NOT EXISTS test_schema (
                id int PRIMARY KEY,
                data text
            )
        """
        )

        # Wait for schema agreement
        agreed = await session.await_schema_agreement()
        assert agreed is True

        # Cleanup
        await session.execute("DROP TABLE IF EXISTS test_schema")

    async def test_get_cluster_data(self, session):
        """Test getting cluster data"""
        cluster_data = session.get_cluster_data()
        assert cluster_data is not None
        assert isinstance(cluster_data, str)
        assert len(cluster_data) > 0

    async def test_invalid_keyspace(self, session):
        """Test using non-existent keyspace"""
        with pytest.raises(ScyllaError):
            await session.use_keyspace("nonexistent_keyspace_12345", False)
