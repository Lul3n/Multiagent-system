import re

def parsear_precios(value):
    if value is None:
        return None

    texto = str(value).strip().lower()

    if texto in ["", "none", "null"]:
        return None

    if "gratuito" in texto:
        return 0.0

    numeros = re.findall(r"\d[\d,]*(?:\.\d+)?", texto)
    if not numeros:
        return None

    valores = []
    for n in numeros:
        try:
            valores.append(float(n.replace(",", "")))
        except ValueError:
            pass

    return sum(valores) / len(valores) if valores else None


def extraer_datos_doctor(doctor):
    calificaciones = []
    for opinion in doctor["opiniones"]:
        try:
            calificacion = float(opinion.get("estrellas"))
            if 1 <= calificacion <= 5:
                calificaciones.append(calificacion)
        except (TypeError, ValueError):
            pass

    precios = []
    for servicio in doctor["servicios"]:
        precio = parsear_precios(servicio.get("precio"))
        if precio is not None:
            precios.append(precio)

    return {
        "suma_estrellas": sum(calificaciones),
        "numero_calificaciones": len(calificaciones),
        "cantidad_servicios": len(doctor["servicios"]),
        "servicios_con_precio": len(precios),
        "precio_promedio": sum(precios) / len(precios) if precios else None,
        "numero_titulos": len(doctor["experiencia"]["formacion"]),
        "enfermedades_tratadas": len(doctor["experiencia"]["enfermedades_tratadas"]),
        "numero_enfoques": len(doctor["experiencia"]["enfoques"]),
        "cantidad_cedulas": len(doctor["cedula"]),
        "cantidad_clinicas": len(doctor["clinicas"]),
        "cantidad_aseguradoras": len(doctor["aseguradoras"]),
        "cantidad_idiomas": len(doctor["experiencia"]["lenguajes"]),
        "cantidad_tipos_paciente": len(doctor["experiencia"]["pacientes"]),
        "texto_perfil": int(bool(doctor["experiencia"]["sobre_mi"])),
    }