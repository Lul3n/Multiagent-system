"""
Agente Scorer de Doctores — Punto de entrada para pipeline E2E.
Evalua y rankea doctores del JSON scrapeado de Doctoralia.
"""
import sys
import json
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# --- asegurar que los imports locales funcionen desde cualquier CWD ---
sys.path.insert(0, str(Path(__file__).resolve().parent))

from limpiar_data import dataset_limpio
from extraer_atributos import extraer_datos_doctor
from puntajes import calcular_contexto_dataset, puntaje_confianza, evaluar_doctor


def buscar_archivo_datos(nombre_explicito=None):
    """Busca el JSON de doctores: argumento > CWD > rutas conocidas."""
    candidatos = []

    if nombre_explicito:
        candidatos.append(Path(nombre_explicito))

    base = Path(__file__).resolve().parent
    candidatos += [
        Path("doctor_data.json"),
        Path("doctor_data.en.json"),
        base / "doctor_data.json",
        base / "doctor_data.en.json",
        base / ".." / ".." / "translator" / "output" / "doctor_data.en.json",
        base / ".." / ".." / "doctor_data.json",
    ]

    for ruta in candidatos:
        if ruta.exists():
            return ruta

    return None


def main():
    archivo_arg = sys.argv[1] if len(sys.argv) > 1 else None
    ruta = buscar_archivo_datos(archivo_arg)

    if ruta is None:
        print("[Scorer Doctores] No se encontro archivo de datos de doctores.")
        print("[Scorer Doctores] Uso: python main.py [ruta_al_json]")
        sys.exit(1)

    print(f"[Scorer Doctores] Cargando datos desde: {ruta}")

    with open(ruta, "r", encoding="utf-8") as f:
        doctores = json.load(f)

    print(f"[Scorer Doctores] {len(doctores)} doctores encontrados. Limpiando datos...")
    doctores = dataset_limpio(doctores)

    # --- Extraer caracteristicas de cada doctor ---
    filas = []
    for doctor in doctores:
        filas.append({
            "doctor": doctor,
            "caracteristicas": extraer_datos_doctor(doctor),
        })

    contexto = calcular_contexto_dataset(filas)

    # --- Evaluar y rankear ---
    clasificacion = []
    for fila in filas:
        puntaje, componentes = evaluar_doctor(
            fila["caracteristicas"],
            contexto
        )
        confianza = puntaje_confianza(fila["caracteristicas"])

        clasificacion.append({
            "doctor": fila["doctor"],
            "caracteristicas": fila["caracteristicas"],
            "puntaje": round(puntaje, 2),
            "confianza": round(confianza, 2),
            "componentes": {k: round(v, 2) if v is not None else None for k, v in componentes.items()},
        })

    clasificacion.sort(key=lambda x: x["puntaje"], reverse=True)

    # --- Imprimir ranking en consola ---
    print(f"\n{'='*60}")
    print(f"  RANKING GENERAL DE LOS MEJORES DOCTORES")
    print(f"  Total evaluados: {len(clasificacion)}")
    print(f"{'='*60}")

    for posicion, elemento in enumerate(clasificacion[:10], start=1):
        doctor = elemento["doctor"]
        print(f"\n  #{posicion} {doctor.get('nombre_doctor', 'Sin nombre')}")
        print(f"     Especialidad: {doctor.get('especialidad', 'N/A')}")
        print(f"     Puntaje: {elemento['puntaje']}/100")
        print(f"     Confianza: {elemento['confianza']}/100")

    if len(clasificacion) > 10:
        print(f"\n  ... y {len(clasificacion) - 10} doctores mas")

    # --- Guardar JSON de salida ---
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "ranking_doctores.json"

    ranking_json = []
    for posicion, elemento in enumerate(clasificacion, start=1):
        doctor = elemento["doctor"]
        ranking_json.append({
            "posicion": posicion,
            "nombre": doctor.get("nombre_doctor", "Sin nombre"),
            "especialidad": doctor.get("especialidad", "N/A"),
            "puntaje": elemento["puntaje"],
            "confianza": elemento["confianza"],
            "componentes": elemento["componentes"],
            "num_opiniones": elemento["caracteristicas"]["numero_calificaciones"],
            "num_servicios": elemento["caracteristicas"]["cantidad_servicios"],
            "num_clinicas": elemento["caracteristicas"]["cantidad_clinicas"],
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ranking_json, f, ensure_ascii=False, indent=2)

    print(f"\n[Scorer Doctores] Ranking guardado en: {output_file}")
    print(f"[Scorer Doctores] Proceso completado exitosamente.")


if __name__ == "__main__":
    main()
