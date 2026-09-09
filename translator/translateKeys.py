import json

KEYS_TO_ENG = {
    "nombre_doctor": "doctor_name",
    "especialidad": "specialty",
    "cedula": "license",
    "experiencia": "experience",
    "formacion":"education",
    "sobre_mi": "about_me",
    "enfermedades_tratadas": "treated_diseases",
    "lenguajes": "languages",
    "enfoques": "approaches",
    "pacientes": "patients",
    "redes_sociales": "social_media",
    "clinicas": "clinics",
    "nombre clinica": "clinic_name",
    "direccion": "address",
    "mapa": "map",
    "telefonos": "phone_numbers",
    "servicios": "services",
    "servicio": "service",
    "precio": "price",
    "aseguradoras": "insurance_companies",
    "opiniones": "reviews",
    "nombre opinion": "review_name",
    "estrellas": "stars",
    "comentario": "comment",
    "fecha": "date",
    "lugar": "place",
    "procedimiento": "procedure",
    "scrap date": "scrape_date",

    "nombre":"name",
    "tipo": "type",
    "precio_total": "total_price",
    "rating": "rating",
    "rating_texto": "text_rating",
    "num_resenas": "reviews_num",
    "checkin": "checkin",
    "checkout": "checkout",
    "vendor": "vendor",
    "link": "link",
    "zona": "area",
    "descripcion_titulo": "description_title",
    "descripcion_texto": "description_text",
    "facilidades_populares": "popular_amenities",
    "property_highlights": "property_highlights",
}

def translateKeys(INPUT_FILE, OUTPUT_FILE):
    with open(INPUT_FILE, 'r', encoding="utf-8") as file:
        data = file.read()

        for oK, nK in KEYS_TO_ENG.items():
            data = data.replace(oK, nK)

        modifiedData = json.loads(data)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(modifiedData, file, indent=4, ensure_ascii=False)

    
def main():
    translateKeys("doctor_data.en.json", "translated_doctor_data.json")
    translateKeys("hoteles_booking_detalle.json", "translated_hotels_data.json")

if __name__ == "__main__":
    main()

