
# Translation scripts

The purpose of these scripts is to translate the JSON data files from spanish into english, with results saved to `output/`.


## Scripts Overview

| File | Function | Does |
| --- | --- | ----- |
| `translate.py` | `translate_doctor_file(INPUT_FILE, OUTPUT_FILE)` | Translates the text content of the JSON file (in the specific structure for the doctor file) while preserving the original structure, keys, non-string values, and proper names. The translation is done by the `translators` package.|
| `translateKeys.py` | `translateKeys(INPUT_FILE, OUTPUT_FILE)` | Translates the keys of a JSON file and outputs them into another JSON file. The translation is done by a static dict.|
| `main.py` | `full_translate()` | Executes the previous functions and leaves the results in the output/ dir.


## Requirements

- Python 3.10+
- [`translators`](https://pypi.org/project/translators/) package

Install dependencies:

```bash
pip install translators
```

## Configuration

Set the following before running `main.py` (as constants at the top of the file, or via environment variables, depending on your setup):

| Setting | Description | Example |
|---|---|---|
| `DOCTOR_DATA_FILE_PATH` | Path + filename to the json with the doctor data | `"doctor_data.json"` |
| `HOTEL_DATA_FILE_PATH` | Path + filename to the json with the hotel data | `"hoteles_booking_detalle.json"` |


## How translate.py works

The script will:

1. Read `INPUT_FILE`.
2. Identify all unique translatable strings.
3. Translate them (one request per unique string, with progress logging).
4. Rebuild the JSON with translations applied.
5. Write the result to `OUTPUT_FILE`.


The script walks the JSON tree, extracts only the strings that should be translated, sends the unique strings off for translation, and then rebuilds the JSON with the translated text spliced back into the original structure.

```
input JSON (spanish)
        │
        ▼
collect_translatable_strings()  -> finds every string worth translating, based on its location in the JSON
        │
        ▼
translate_strings()             -> translates each unique string
        │
        ▼
apply_translations()            -> rebuilds the JSON with translated text in place
        │
        ▼
output JSON (english)
```