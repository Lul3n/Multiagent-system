import json
import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from limpiarDatos import limpiarLista, neutro
from scoring import calcularScore, rank


def encontrar_archivo_datos():
    """Busca el archivo de hoteles en rutas comunes locales o del pipeline."""
    if len(sys.argv) > 1:
        custom_path = Path(sys.argv[1])
        if custom_path.exists():
            return custom_path

    posibles_rutas = [
        Path("hoteles_booking_detalle.json"),
        Path("hotel_data.en.json"),
        current_dir / "hoteles_booking_detalle.json",
        current_dir / "hotel_data.en.json",
        current_dir.parent.parent / "translator" / "output" / "hotel_data.en.json",
        Path("translator/output/hotel_data.en.json"),
        Path("output/hotel_data.en.json"),
    ]

    for ruta in posibles_rutas:
        if ruta.exists():
            return ruta
    return None


def main():
    archivo = encontrar_archivo_datos()
    if not archivo:
        print("[Scorer Hoteles] Advertencia: No se encontró ningún archivo de datos de hoteles para rankear.")
        return

    print(f"[Scorer Hoteles] Cargando datos desde: {archivo}")
    with open(archivo, "r", encoding="utf-8") as f:
        hoteles = json.load(f)

    if not hoteles:
        print("[Scorer Hoteles] Archivo vacío, terminando.")
        return

    hoteles_limpios = limpiarLista(hoteles)
    neutro(hoteles_limpios)

    # preferencias por defecto
    amenidades_pedidas = {
        "beachfront": 5,
        "pool": 3,
        "wifi": 2,
        "ac": 3,
        "restaurant": 2,
        "parking": 1,
    }

    calcularScore(hoteles_limpios, amenidades_pedidas)
    ranking = rank(hoteles_limpios)

    # Serializar amenidades como listas para JSON
    ranking_export = []
    for h in ranking:
        item = dict(h)
        if isinstance(item.get("amenidades"), set):
            item["amenidades"] = sorted(list(item["amenidades"]))
        ranking_export.append(item)

    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "ranking_hoteles.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(ranking_export, f, ensure_ascii=False, indent=2)

    print(f"\n========================================================")
    print(f"   RANKING DE HOTELES ({len(ranking)} hoteles evaluados)")
    print(f"========================================================")
    for pos, hotel in enumerate(ranking[:10], start=1):
        print(f"#{pos:02d} | {hotel['nombre']}")
        print(f"     Zona: {hotel['zona']} | Tipo: {hotel['tipo']} | Precio: {hotel['moneda']} {hotel['precio']:,.2f}")
        print(f"     Score Final: {hotel['scoreFinal'] * 100:.1f}/100 (Rating: {hotel['scoreRating']*100:.0f}%, Precio: {hotel['scorePrecio']*100:.0f}%, Amenidades: {hotel['scoreAmenidades']*100:.0f}%)")
        amenidades_str = ', '.join(sorted(list(hotel['amenidades']))) if hotel['amenidades'] else 'Ninguna'
        print(f"     Amenidades detectadas: {amenidades_str}")
        print("-" * 56)

    print(f"\n[Scorer Hoteles] Ranking guardado exitosamente en: {out_file}")


if __name__ == "__main__":
    main()
