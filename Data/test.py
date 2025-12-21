from fastapi.testclient import TestClient
from main import app  # Assure-toi que ton fichier API s'appelle main.py

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict():
    sample_data = {
        "surface": 100.0,
        "nombre_de_pieces": 3,
        "nombre_de_chambres": 2,
        "nombre_de_salles_de_bain": 2,
        "etage": 1,
        "terrasse": 0,
        "garage": 1,
        "ascenseur": 0,
        "piscine": 0,
        "securite": 1,
        "type_bien": "appartement",
        "ville": "casablanca",
        "quartier": "maarif"
    }

    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200
    json_data = response.json()

    print("💰 Prix estimé:", json_data["formatted_price"])

    assert "predicted_price_MAD" in json_data
    assert json_data["predicted_price_MAD"] > 0

