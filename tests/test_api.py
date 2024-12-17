import pytest
from fastapi import status
from pathlib import Path
import io
from PIL import Image
import numpy as np

def create_test_image():
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_process_image(client):
    # Test image processing endpoint
    files = {
        'file': ('test.jpg', create_test_image(), 'image/jpeg')
    }
    response = client.post("/api/process-image", files=files)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "success" in data
    assert "detections" in data

def test_add_language(client):
    # Test adding a new language
    language_data = {
        "code": "xho",
        "name": "isiXhosa",
        "region": "South Africa"
    }
    response = client.post("/api/languages", json=language_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["code"] == language_data["code"]

def test_add_term(client):
    # First add a language
    language_response = client.post("/api/languages", json={
        "code": "xho",
        "name": "isiXhosa",
        "region": "South Africa"
    })
    language_id = language_response.json()["id"]

    # Test adding a new term
    term_data = {
        "language_id": language_id,
        "object_id": 1,
        "term": "umthi",
        "pronunciation": "um-thi",
        "context": "Tree in isiXhosa"
    }
    response = client.post("/api/terms", json=term_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["term"] == term_data["term"]

def test_get_terms(client):
    # Add a language and term first
    language_response = client.post("/api/languages", json={
        "code": "xho",
        "name": "isiXhosa",
        "region": "South Africa"
    })
    language_id = language_response.json()["id"]

    term_data = {
        "language_id": language_id,
        "object_id": 1,
        "term": "umthi",
        "pronunciation": "um-thi"
    }
    client.post("/api/terms", json=term_data)

    # Test getting terms for a language
    response = client.get(f"/api/terms/xho")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_statistics(client):
    response = client.get("/api/statistics")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_images" in data
    assert "total_terms" in data
    assert "total_languages" in data
    assert "recent_contributions" in data