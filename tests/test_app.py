# AI-Ticker Tests
import pytest
from app import app


@pytest.fixture
def client():
    """Creates a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Checks if the main page loads correctly."""
    response = client.get('/')
    if response.status_code != 200:
        raise AssertionError(f"Expected status code 200, got {response.status_code}")
    if b"<!DOCTYPE html>" not in response.data:
        raise AssertionError("Expected HTML DOCTYPE in response")


def test_api_message_route(client):
    """Checks if the API returns a JSON response."""
    response = client.get('/api/message')
    if response.status_code != 200:
        raise AssertionError(f"Expected status code 200, got {response.status_code}")
    if not response.is_json:
        raise AssertionError("Expected JSON response")
