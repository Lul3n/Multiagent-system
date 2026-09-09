import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json
import time
import random

# ---- Configuración ----
# Mientras no decidas si quieres el detalle de los 80 o solo un subconjunto,
# deja LIMITE en un número chico (5-10) para probar sin quemar tiempo/requests.
LIMITE = 64

with open("hoteles_booking.json", "r", encoding="utf-8") as f:
    hoteles = json.load(f)

driver = uc.Chrome()

def extraer_descripcion(soup):
    cont = soup.find(attrs={"data-testid": "property-description"})
    if not cont:
        return None, None

    # El título en negritas suele ser el primer h2/h3/strong dentro del contenedor
    titulo_tag = cont.find(["h2", "h3", "strong", "b"])
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else None

    # El resto: todos los <p> dentro del contenedor, unidos
    parrafos = cont.find_all("p")
    if parrafos:
        texto = "\n".join(p.get_text(strip=True) for p in parrafos if p.get_text(strip=True))
    else:
        # fallback: todo el texto del contenedor menos el título
        texto_completo = cont.get_text("\n", strip=True)
        texto = texto_completo.replace(titulo, "", 1).strip() if titulo else texto_completo

    return titulo, texto


def extraer_facilidades_populares(soup):
    cont = soup.find(attrs={"data-testid": "property-most-popular-facilities-wrapper"})
    if not cont:
        return []
    # normalmente son <li> o <span> dentro del wrapper
    items = [li.get_text(" ", strip=True) for li in cont.find_all("li")]
    if not items:
        items = [s.get_text(" ", strip=True) for s in cont.find_all("span") if s.get_text(strip=True)]
    return [i for i in items if i]


def extraer_highlights(soup):
    # Confirmado por inspección real: es class="property-highlights", NO data-testid.
    cont = soup.find("div", class_="property-highlights")
    if not cont:
        return []
    items = [li.get_text(" ", strip=True) for li in cont.find_all("li", class_="ph-content")]
    return [i for i in items if i]


hoteles_con_link = [h for h in hoteles if h.get("link")][:LIMITE]
print(f"Procesando {len(hoteles_con_link)} hoteles (de {len(hoteles)} totales, LIMITE={LIMITE})")

for i, hotel in enumerate(hoteles_con_link):
    print(f"[{i+1}/{len(hoteles_con_link)}] {hotel['nombre']}")
    try:
        driver.get(hotel["link"])
        time.sleep(random.uniform(4, 7))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        titulo, texto = extraer_descripcion(soup)
        hotel["descripcion_titulo"] = titulo
        hotel["descripcion_texto"] = texto
        hotel["facilidades_populares"] = extraer_facilidades_populares(soup)
        hotel["property_highlights"] = extraer_highlights(soup)

    except Exception as e:
        print(f"  Error en {hotel['nombre']}: {type(e).__name__}: {e}")
        hotel["descripcion_titulo"] = None
        hotel["descripcion_texto"] = None
        hotel["facilidades_populares"] = []
        hotel["property_highlights"] = []

    time.sleep(random.uniform(2, 4))

    # Checkpoint: guarda cada 10 hoteles para no perder el progreso si algo truena
    if (i + 1) % 10 == 0:
        with open("hoteles_booking_detalle.json", "w", encoding="utf-8") as f:
            json.dump(hoteles, f, ensure_ascii=False, indent=2)
        print(f"  [checkpoint guardado en hotel {i+1}]")

driver.quit()

with open("hoteles_booking_detalle.json", "w", encoding="utf-8") as f:
    json.dump(hoteles, f, ensure_ascii=False, indent=2)

print("\nListo. Guardado en hoteles_booking_detalle.json")
sin_descripcion = sum(1 for h in hoteles_con_link if not h.get("descripcion_texto"))
print(f"Hoteles sin descripción extraída: {sin_descripcion}/{len(hoteles_con_link)}")