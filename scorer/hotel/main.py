import json
from pathlib import Path
from limpiarDatos import limpiarLista, neutro
from scoring import calcularScore, rank

ARCHIVODATOS = Path("hoteles_booking_detalle.json")
def cargarDatos():
    with open(ARCHIVODATOS, "r", encoding="utf-8") as archivo:
        return json.load(archivo)

def main():
    hoteles = cargarDatos()
    hoteles = limpiarLista(hoteles)
    neutro(hoteles)
    
    # amenidades pedidas de prueba
    amenidadesPedidas = {
        "beachfront": 5,
        "pool": 3,
        "pet": 4,
        "wifi": 1
    }

    calcularScore(hoteles, amenidadesPedidas)
    resultado = rank(hoteles)

    print(f"RANKING HOTELES\nNUMERO DE HOTELES {len(resultado)}\n")
    for posicion, hotel in enumerate(resultado, start=1):
        print(f"\n #{posicion} {hotel['nombre']}")
        print(f"ZONA: {hotel['zona']}")
        print(f"TIPO: {hotel['tipo']}")
        print(f"PRECIO: {hotel['moneda']} {hotel['precio']:.2f}")
        print(f"PUNTAJE GENERAL: {hotel['scoreFinal'] * 100:.2f}/100")

        print("PUNTUACIÓN POR CATEGORIA:")
        componentes = {
            "Rating": hotel["scoreRating"],
            "Precio": hotel["scorePrecio"],
            "Reseñas": hotel["scoreResenas"],
            "Amenidades": hotel["scoreAmenidades"],
        }
        for nombre, valor in componentes.items():
            print(f"    {nombre}: {valor * 100:.2f}")

        print(
            f"    Opiniones: {hotel['numResenas']}"
            f"\n    Amenidades ofrecidas: {len(hotel['amenidades'])}"
        )

main()

