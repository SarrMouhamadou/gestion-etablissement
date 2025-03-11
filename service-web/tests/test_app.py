import json
import unittest.mock as mock

def test_index_route(client, mocker):
    """Teste la route / avec un mock des appels HTTP."""
    mock_response = mocker.patch('requests.get')
    mock_response.return_value.status_code = 200
    mock_response.return_value.json.return_value = [{"id": 1, "nom": "Test"}]  # Simuler une réponse

    response = client.get('/')
    assert response.status_code == 200
    assert b'total_etudiants' in response.data

def test_login_route_get(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Connexion' in response.data

def test_login_route_post_success(client):
    data = {'username': 'admin', 'password': 'admin'}
    response = client.post('/login', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Connexion reussie' in response.data

def test_login_route_post_failure(client):
    data = {'username': 'admin', 'password': 'mauvais_mot_de_passe'}
    response = client.post('/login', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Nom d\utilisateur ou mot de passe incorrect' in response.data

def test_list_etudiants_route(client, mocker):
    mock_response = mocker.patch('requests.get')
    mock_response.return_value.status_code = 200
    mock_response.return_value.json.return_value = [{"matricule": "E001", "nom": "Jean", "classe_id": 1}]

    response = client.get('/etudiants')
    assert response.status_code == 200
    assert b'Liste des etudiants' in response.data