import pytest
from app.main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_hello_route(client):
    """Testa a rota principal"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json['message'] == 'Bem-vindo ao DEVOPS-LAB-AWS'
    assert response.json['status'] == 'success'

def test_health_route(client):
    """Testa a rota de health check"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_404_route(client):
    """Testa rota não existente"""
    response = client.get('/nonexistent')
    assert response.status_code == 404
