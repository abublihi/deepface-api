import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Local image paths
REAL_IMAGE_PATH = "tests/real_face.jpg"
REAL_IMAGE_2_PATH = "tests/real_face2.jpg"
SPOOFED_IMAGE_PATH = "tests/spoofed_face.jpg"

def test_represent_real_image():
    with open(REAL_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/represent",
            files={"img": ("real_face.jpg", f, "image/jpeg")},
            params={"anti_spoofing": "true"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "embedding" in data[0]

def test_represent_spoofed_image():
    with open(SPOOFED_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/represent",
            files={"img": ("spoofed_face.jpg", f, "image/jpeg")},
            params={"anti_spoofing": "true"}
        )
    assert response.status_code == 422
    data = response.json().get('detail')
    assert data.get('spoofed') is True
    assert "Spoofed image detected" in data.get("message", "")

def test_analyze_real_image():
    with open(REAL_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/analyze",
            files={"img": ("real_face.jpg", f, "image/jpeg")},
            params={"anti_spoofing": "true"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "age" in data[0] or "dominant_gender" in data[0]

def test_analyze_spoofed_image():
    with open(SPOOFED_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/analyze",
            files={"img": ("spoofed_face.jpg", f, "image/jpeg")},
            params={"anti_spoofing": "true"}
        )
    assert response.status_code == 422
    data = response.json().get('detail')
    assert data.get("spoofed") is True
    assert "Spoofed image detected" in data.get("message", "")

def test_verify_real_matched_images():
    with open(REAL_IMAGE_PATH, "rb") as f1, open(REAL_IMAGE_PATH, "rb") as f2:
        files = {
            "img1": ("real_face.jpg", f1, "image/jpeg"),
            "img2": ("real_face.jpg", f2, "image/jpeg"),
        }
        response = client.post(
            "/verify",
            files=files,
            params={"anti_spoofing": "true"}
        )
    assert response.status_code == 200
    assert response.json().get('verified') == True

def test_verify_real_unmatched_images():
    with open(REAL_IMAGE_PATH, "rb") as f1, open(REAL_IMAGE_2_PATH, "rb") as f2:
        files = {
            "img1": ("real_face.jpg", f1, "image/jpeg"),
            "img2": ("real_face2.jpg", f2, "image/jpeg"),
        }
        response = client.post(
            "/verify",
            files=files,
            params={"anti_spoofing": "true"}
        )
    print(response)
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert response.json().get('verified') == False

def test_verify_with_spoofed_image():
    with open(REAL_IMAGE_PATH, "rb") as f1, open(SPOOFED_IMAGE_PATH, "rb") as f2:
        files = {
            "img1": ("real_face.jpg", f1, "image/jpeg"),
            "img2": ("spoofed_face.jpg", f2, "image/jpeg"),
        }
        response = client.post(
            "/verify",
            files=files,
            params={"anti_spoofing": "true"}
        )
    assert response.status_code == 500
    assert "Exception while processing" in response.json().get("detail", "")

def test_disable_anti_spoofing_allows_spoofed_image():
    with open(SPOOFED_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/represent",
            files={"img": ("spoofed_face.jpg", f, "image/jpeg")},
            params={"anti_spoofing": "false"}
        )
    assert response.status_code == 200
