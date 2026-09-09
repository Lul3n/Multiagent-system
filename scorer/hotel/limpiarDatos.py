from atributos import precio, calif, resenas, extraerAmenidades

def limpiarHotel(hotel):
    precio_raw = hotel.get("precio_total") or hotel.get("price_total")
    rating_raw = hotel.get("rating")
    resenas_raw = hotel.get("num_resenas") or hotel.get("reviews_num")

    moneda, monto = precio(precio_raw) if precio_raw else ("MXN", 0.0)
    rating = calif(rating_raw)
    numResenas = resenas(resenas_raw)
    amenidades = extraerAmenidades(hotel)

    newHotel = {    
                "nombre": hotel.get("nombre") or hotel.get("name"),
                "link": hotel.get("link"),
                "zona": hotel.get("zona") or hotel.get("area"),
                "tipo": hotel.get("tipo") or hotel.get("type"),
                "vendor": hotel.get("vendor"),
                "precio": monto,
                "moneda": moneda,
                "rating": rating,
                "ratingNulo": False,
                "numResenas": numResenas,
                "amenidades": amenidades
            }
    return newHotel

def limpiarLista(hoteles):
    newHoteles = []
    for hotel in hoteles:
        newHoteles.append(limpiarHotel(hotel))
    return newHoteles

def neutro(hoteles):
    avgRating = 0.0
    avgLen = len(hoteles)
    for hotel in hoteles:
        if hotel["rating"] is None:
            avgRating += 0
            hotel["ratingNulo"] = True
            avgLen -= 1
        else:
            avgRating += hotel["rating"]
    # en el caso poco probable de que todos los ratings sean nulos.
    # se esta asumiendo que la escala de rating es 0-10, pero en caso de consultar mas vendedores, se ajusta con el
    # diccionario de ESCALAS.
    if avgLen == 0:
        avgRating = 5.0
    else:
        avgRating /= avgLen
    for hotel in hoteles:
        if hotel["rating"] is None:
            hotel["rating"] = avgRating

