from app.model import predict_price

def test_predict_price_type():
    # Vérifie que la fonction retourne un nombre
    result = predict_price({'surface': 50, 'chambres': 2})
    assert isinstance(result, (int, float))

def test_predict_price_positive():
    # Vérifie que le prix prédit n'est pas négatif
    result = predict_price({'surface': 50, 'chambres': 2})
    assert result >= 0
