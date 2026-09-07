from translate import translate_doctor_file
from translateKeys import translateKeys
from pathlib import Path

DOCTOR_DATA_FILE_PATH = "doctor_data.json"
HOTEL_DATA_FILE_PATH = "hoteles_booking_detalle.json"

def full_translate():
    outpath = Path("output")
    translate_doctor_file(DOCTOR_DATA_FILE_PATH, outpath / "doctor_data.en.json")
    translateKeys(outpath / "doctor_data.en.json", outpath / "doctor_data.en.json")
    translateKeys(HOTEL_DATA_FILE_PATH, outpath / "hotel_data.en.json")

def main():
    full_translate()


if __name__ == "__main__":
    main()