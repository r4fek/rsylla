#!/bin/bash

set -e

echo "========================================="
echo "rsylla Test Suite"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if library is built
echo "Checking if library is built..."
if ! python3 -c "import rsylla" 2>/dev/null; then
    echo -e "${YELLOW}Library not built. Building with maturin...${NC}"
    if ! command -v maturin &> /dev/null; then
        echo -e "${RED}maturin not found. Installing...${NC}"
        pip install maturin
    fi
    maturin develop
    echo -e "${GREEN}Library built successfully${NC}"
else
    echo -e "${GREEN}Library already built${NC}"
fi

echo ""

# Check if docker is running
echo "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}Docker is running${NC}"

echo ""

# Start ScyllaDB
echo "Starting ScyllaDB with docker compose..."
docker compose down -v 2>/dev/null || true
docker compose up -d

echo ""
echo "Waiting for ScyllaDB to be ready..."
echo "This may take up to 2 minutes..."

# Wait for ScyllaDB to be healthy
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker compose exec -T scylla cqlsh -e "describe cluster" > /dev/null 2>&1; then
        echo -e "${GREEN}ScyllaDB is ready!${NC}"
        break
    fi

    attempt=$((attempt + 1))
    echo -n "."
    sleep 2

    if [ $attempt -eq $max_attempts ]; then
        echo -e "\n${RED}ScyllaDB failed to start within expected time${NC}"
        echo "Checking logs:"
        docker compose logs scylla
        exit 1
    fi
done

echo ""
echo ""

# Install test requirements
echo "Installing test requirements..."
pip install -q -r requirements-test.txt
echo -e "${GREEN}Test requirements installed${NC}"

echo ""

# Run tests
echo "========================================="
echo "Running Tests"
echo "========================================="
echo ""

# Run pytest with nice output
pytest tests/ -v --tb=short -m integration

TEST_EXIT_CODE=$?

echo ""
echo "========================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed!${NC}"
fi

echo "========================================="
echo ""

# Ask if user wants to stop ScyllaDB
read -p "Stop ScyllaDB container? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping ScyllaDB..."
    docker compose down
    echo -e "${GREEN}ScyllaDB stopped${NC}"
else
    echo "ScyllaDB is still running. Stop it with: docker compose down"
fi

exit $TEST_EXIT_CODE
