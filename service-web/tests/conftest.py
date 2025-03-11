import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import bcrypt
from app import app as flask_app, db, User

@pytest.fixture
def client():
    # Configurer l'application pour utiliser une base de données de test PostgreSQL
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:passer@localhost:5432/dbweb_test'
    with flask_app.app_context():
        db.create_all()  # Créer les tables
        # Vérifier si l'utilisateur admin existe déjà
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_user = User(username='admin', password=hashed_password)
            db.session.add(admin_user)
            db.session.commit()
        yield flask_app.test_client()
        db.drop_all()  # Nettoyer les tables après les tests

@pytest.fixture
def mocker(monkeypatch):
    import unittest.mock
    return unittest.mock.MagicMock()