from bs4 import BeautifulSoup
import json
import re

with open("resultado_selenium.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

hoteles = []
tarjetas = soup.find_all(attrs={"data-testid": "property-card"})

palabras_hotel = ["hotel", "suites", "resort", "motel", "inn", "spa", "beach club"]

def clasificar(nombre):
    nombre_lower = nombre.lower()
    for palabra in palabras_hotel:
        if palabra in nombre_lower:
            return "hotel"
    return "departamento_o_condominio"

def extraer_rating(tarjeta):
    """
    SUPOSICIÓN: Booking suele meter la calificación en un bloque
    data-testid="review-score". Si esto ya no coincide con el HTML real,
    imprime tarjeta.prettify() de una sola tarjeta para ver la estructura
    actual y ajusta el selector.
    """
    rating_tag = tarjeta.find(attrs={"data-testid": "review-score"})
    if not rating_tag:
        return None, None, None

    texto = rating_tag.get_text(" ", strip=True)

    # Score tipo "8,7" o "8.7"
    score_match = re.search(r"\b\d[.,]\d\b", texto)
    score = score_match.group(0).replace(",", ".") if score_match else None

    # Palabra de calificación: "Fabuloso", "Muy bien", "Excelente", etc.
    palabra_match = re.search(
        r"(Excepcional|Fabuloso|Muy bien|Bien|Estupendo|Excelente|Fantástico|"
        r"Exceptional|Fabulous|Very good|Good|Wonderful|Superb)",
        texto, re.I
    )
    palabra = palabra_match.group(0) if palabra_match else None

    # Número de reseñas: "1,234 comentarios" / "234 reviews"
    conteo_match = re.search(r"([\d.,]+)\s*(comentarios|reseñas|reviews|opiniones)", texto, re.I)
    conteo = conteo_match.group(1) if conteo_match else None

    return score, palabra, conteo


for tarjeta in tarjetas:
    nombre_tag = tarjeta.find(attrs={"data-testid": "title"})
    precio_tag = tarjeta.find(attrs={"data-testid": "price-and-discounted-price"})
    link_tag = tarjeta.find("a", attrs={"data-testid": "title-link"})

    nombre = nombre_tag.get_text(strip=True) if nombre_tag else None
    precio_limpio = None
    if precio_tag:
        precio_limpio = precio_tag.get_text(strip=True).replace("\xa0", " ")

    link = link_tag.get("href") if link_tag else None
    if link and link.startswith("/"):
        link = "https://www.booking.com" + link

    rating_score, rating_palabra, num_resenas = extraer_rating(tarjeta)

    hoteles.append({
        "nombre": nombre,
        "tipo": clasificar(nombre) if nombre else None,
        "precio_total": precio_limpio,
        "rating": rating_score,
        "rating_texto": rating_palabra,
        "num_resenas": num_resenas,
        "checkin": "2026-09-15",
        "checkout": "2026-09-22",
        "vendor": "Booking.com",
        "link": link,
        "zona": "San Carlos, Sonora"
    })

with open("hoteles_booking.json", "w", encoding="utf-8") as f:
    json.dump(hoteles, f, ensure_ascii=False, indent=2)

print(f"Se guardaron {len(hoteles)} alojamientos")
sin_rating = sum(1 for h in hoteles if h["rating"] is None)
print(f"Sin rating detectado: {sin_rating}/{len(hoteles)}")
for h in hoteles:
    rating_str = h["rating"] or "s/r"
    print(f"{h['tipo']:<25} | {h['precio_total']:<15} | rating: {rating_str:<5} | {h['nombre']}")