import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import app


def test_index_loads():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200


def test_form_creates_message():
    client = app.test_client()
    response = client.post('/mensajes', data={
        'nombre': 'Test',
        'email': 'test@example.com',
        'mensaje': 'Mensaje de prueba'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Mensaje guardado correctamente.' in response.data
