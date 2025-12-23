from app.main import predict_price, UserInput

def test_predict_price_type():
    user = UserInput(
        surface=50,
        nombre_de_chambres=2,
        nombre_de_salles_de_bain=1,
        etage=2,
        terrasse=0,
        garage=1,
        ascenseur=1,
        piscine=0,
        securite=1,
        type_bien="appartement",
        ville="Casablanca",
        quartier="Maarif"
    )

    result = predict_price(user)
    assert isinstance(result["predicted_price_MAD"], float)


def test_predict_price_positive():
    user = UserInput(
        surface=60,
        nombre_de_chambres=3,
        nombre_de_salles_de_bain=2,
        etage=3,
        terrasse=1,
        garage=1,
        ascenseur=1,
        piscine=0,
        securite=1,
        type_bien="appartement",
        ville="Casablanca",
        quartier="Gauthier"
    )

    result = predict_price(user)
    assert result["predicted_price_MAD"] >= 0
