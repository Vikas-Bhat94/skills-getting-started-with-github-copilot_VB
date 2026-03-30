import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fresh TestClient for each test"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    from copy import deepcopy
    from src import app

    # Store original activities
    original_activities = deepcopy(app.activities)

    yield

    # Restore after test
    app.activities = deepcopy(original_activities)