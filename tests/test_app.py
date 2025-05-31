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
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data

def test_api_message_route(client):
    """Checks if the API returns a JSON response."""
    response = client.get('/api/message')
    assert response.status_code == 200
    assert response.is_json
