from translate import translate_doctor_file
from translateKeys import translateKeys
from pathlib import Path

DOCTOR_DATA_FILE_PATH = "doctor_data.json"
HOTEL_DATA_FILE_PATH = "hoteles_booking_detalle.json"

def full_translate():
    outpath = Path("output")
    outpath.mkdir(parents=True, exist_ok=True)

    # --- Traducción de doctores ---
    translate_doctor_file(DOCTOR_DATA_FILE_PATH, outpath / "doctor_data.en.json")
    translateKeys(outpath / "doctor_data.en.json", outpath / "doctor_data.en.json")

    # --- Traducción de hoteles (si el archivo existe) ---
    if Path(HOTEL_DATA_FILE_PATH).exists():
        print(f"[Traductor] Traduciendo datos de hoteles: {HOTEL_DATA_FILE_PATH}")
        translateKeys(HOTEL_DATA_FILE_PATH, outpath / "hotel_data.en.json")
    else:
        print(f"[Traductor] Archivo de hoteles no encontrado ({HOTEL_DATA_FILE_PATH}), saltando traducción de hoteles.")

def main():
    full_translate()


if __name__ == "__main__":
    main()