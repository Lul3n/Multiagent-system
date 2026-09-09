# si se llegan a usar otros vendores, se llena este diccionario con sus escalas correspondientes.
# pero por el momento no se usa este diccionario
ESCALAS = {
        "Booking.com": 10
}
# umbral de reseñas. en el caso de los hoteles que se tienen, la mayoria de los hoteles
# tienen entre 2 y 50 reseñas.
UMBRALR = 50

def rangoPrecios(hoteles):
    minPrecio = hoteles[0]["precio"]
    maxPrecio = hoteles[0]["precio"]
    for hotel in hoteles:
        minPrecio = min(minPrecio, hotel["precio"]) 
        maxPrecio = max(maxPrecio, hotel["precio"])
    return minPrecio, maxPrecio

def scoreRating(hotel):
    # leer el diccionario de ESCALAS si se piensan mas vendores que booking.com 
    escala = 10 
    return hotel["rating"] / escala

def scoreResenas(hotel):
    if hotel["numResenas"] is None:
        return 0.5
    return min(1.0, hotel["numResenas"] / UMBRALR)

def scorePrecio(hotel, minPrecio, maxPrecio):
    if minPrecio == maxPrecio:
        return 1.0
    return (1 - (hotel["precio"] - minPrecio) / (maxPrecio - minPrecio))

def scoreAmenidades(hotel, amenidadesPedidas):
    # amenidades pedidas es un set con la amenidad que pide el usuario y un peso asignado por el
    # por ejemplo si un usuario busca un hotel y prefiere que sea frenteplaya, pero no le importa tanto
    # que tenga alberca, seria algo como
    # amenidadesPedidas = {"beachfront": 5, "pool": 2}
    # tengo pensado que el peso no lo asigna directo el usuario, si no que rankea amenidades
    # de 1 a n y de ahi se asigna un peso.
    n = sum(amenidadesPedidas.values())
    if n == 0:
        return 1.0
    sumAmenidades = 0
    for categoria, peso in amenidadesPedidas.items():
        if categoria in hotel["amenidades"]:
            sumAmenidades += peso
    return sumAmenidades / n

PESOS = {
        "scoreRating": 0.30,
        "scoreAmenidades": 0.30,
        "scorePrecio": 0.25,
        "scoreResenas": 0.15
}

def calcularScore(hoteles, amenidadesPedidas):
    minPrecio, maxPrecio = rangoPrecios(hoteles)
    for hotel in hoteles:
        hotel["scoreRating"] = scoreRating(hotel)
        hotel["scoreResenas"] = scoreResenas(hotel)
        hotel["scorePrecio"] = scorePrecio(hotel, minPrecio, maxPrecio)
        hotel["scoreAmenidades"] = scoreAmenidades(hotel, amenidadesPedidas)

def scoreFinal(hotel):
    score = 0
    for criterio, peso in PESOS.items():
        score += hotel[criterio] * peso
    return score

def rank(hoteles):
    for hotel in hoteles:
        hotel["scoreFinal"] = scoreFinal(hotel)
    return sorted(hoteles, key=lambda h: h["scoreFinal"], reverse=True)

