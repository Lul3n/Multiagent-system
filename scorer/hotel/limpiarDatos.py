from atributos import precio, calif, resenas, extraerAmenidades

def limpiarHotel(hotel):
    moneda, monto = precio(hotel["precio_total"])
    rating = calif(hotel["rating"])
    numResenas = resenas(hotel["num_resenas"])
    amenidades = extraerAmenidades(hotel)

    newHotel = {    
                "nombre": hotel.get("nombre"),
                "link": hotel.get("link"),
                "zona": hotel.get("zona"),
                "tipo": hotel.get("tipo"),
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

