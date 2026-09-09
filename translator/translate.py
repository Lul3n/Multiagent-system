import json
from pathlib import Path
from typing import Any

import time
import translators as ts

SOURCE_LANGUAGE = "es"
TARGET_LANGUAGE = "en"

# ---------------------------------------------------------
# Fields/subtrees that must NEVER be translated
# ---------------------------------------------------------

PROTECTED_ROOT_FIELDS = {
    "nombre_doctor",
    "cedula",
    "scrap date",
    "aseguradoras"
}

PROTECTED_EXPERIENCIA_FIELDS = {
    "formacion",
    "sobre_mi",
    "redes_sociales",
}

PROTECTED_OPINION_FIELDS = {
    "nombre opinion",
    "estrellas",
    "lugar",
}


# ---------------------------------------------------------
# Determine whether a particular value should be translated
# ---------------------------------------------------------

def should_translate(path: tuple[Any, ...]) -> bool:
    if not path:
        return False

    first = path[1]

    if first in PROTECTED_ROOT_FIELDS:
        return False

    if first == "clinicas":
        return False

    if first == "experiencia" and len(path) >= 3:
        second = path[2]
        
        if second in PROTECTED_EXPERIENCIA_FIELDS:
            return False
        
    if first == "opiniones" and len(path) >= 4:
        last_field = path[3]

        if last_field in PROTECTED_OPINION_FIELDS:
            return False

    return True


# ---------------------------------------------------------
# Collect translatable strings
# ---------------------------------------------------------

def collect_translatable_strings(
    value: Any,
    path: tuple[Any, ...] = (),
    translations: dict[str, str] | None = None,
) -> dict[str, str]:

    if translations is None:
        translations = {}

    # String
    if isinstance(value, str):

        #print(f"[TRANSLATE CHECK] [{path}] [{value}]", end=' ')
        if should_translate(path) and not value.startswith("$"):
            translations[value] = value
            #print(f"PASS <<<<<<<<<<")

        return translations

    # Dictionary
    if isinstance(value, dict):

        for key, child in value.items():
            collect_translatable_strings(
                child,
                path + (key,),
                translations,
            )

        return translations

    # List
    if isinstance(value, list):

        for index, child in enumerate(value):
            collect_translatable_strings(
                child,
                path + (index,),
                translations,
            )

    return translations


# ---------------------------------------------------------
# Replace original strings with translated strings
# ---------------------------------------------------------

def apply_translations(
    value: Any,
    translations: dict[str, str],
    path: tuple[Any, ...] = (),
) -> Any:

    # String
    if isinstance(value, str):
        if should_translate(path):
            return translations.get(value, value)
        return value

    # Dictionary
    if isinstance(value, dict):

        return {
            key: apply_translations(
                child,
                translations,
                path + (key,),
            )
            for key, child in value.items()
        }

    # List
    if isinstance(value, list):

        return [
            apply_translations(
                child,
                translations,
                path + (index,),
            )
            for index, child in enumerate(value)
        ]

    # Numbers, booleans, None, etc.
    return value


# ---------------------------------------------------------
# Translate unique strings using translate-json
# ---------------------------------------------------------

def translate_strings(strings: dict[str, str]) -> dict[str, str]:

    result = {}

    translateTotal = len(strings)
    i = 0
    start_time = time.perf_counter()

    for key in strings.keys():
        i += 1
        if strings[key].startswith("Desde $"):
            result[key] = f"Starting at ${strings[key].removeprefix('Desde $')}"
            continue

        try:
            translatedText = ts.translate_text(strings[key], from_language=SOURCE_LANGUAGE, to_language=TARGET_LANGUAGE, translator="google")
        except Exception as e:
            print(f"FAILED [{(time.perf_counter() - start_time):.1f}s] ({i}/{translateTotal}): \t[{key}] -> {e}")
            translatedText = strings[key]
            time.sleep(5)
            continue
        result[key] = translatedText
        print(f"DONE   [{(time.perf_counter() - start_time):.1f}s] ({i}/{translateTotal}): ", end="\t")
        print(f"[{key}] -> {translatedText}")
        time.sleep(3)
        
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Translation done in: {elapsed_time:.1f} seconds\n")

    return result

    


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def translate_doctor_file(INPUT_FILE = "doctor_data.json", OUTPUT_FILE = "doctor_data.en.json"):
    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    print(f"Reading: {input_path}")

    with input_path.open("r", encoding="utf-8") as file:
        doctor_data = json.load(file)

    print("Finding translatable strings...")

    strings = collect_translatable_strings(doctor_data)

    print(f"Found {len(strings)} unique strings to translate.")

    print("Translating...")

    translations = translate_strings(strings)

    print("Applying translations...")

    translated_data = apply_translations(
        doctor_data,
        translations,
    )

    print(f"Writing: {output_path}")

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            translated_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("Done!")


if __name__ == "__main__":
    translate_doctor_file()