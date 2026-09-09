# ESTE ARCHIVO SOLO ES UNICAMENTE PARA FUNCIONES QUE LIMPIAN LA INFORMACIÓN DEL JSON, HAY MUCHAS IRREGULARIDADES CON LA INFORMACIÓN
# AL IGUAL QUE DATOS NULOS, LAS FUNCIONES SON BASTANTE SENCILLAS PERO IGUAL LAS EXPLICARE BREVEMENTE

# Funcion que verifica si un valor es nulo o una lista esta vacia. Tambien verifica que el dato tampoco sea una "forma" de decir nulo sin ser nulo, 
# como un string vacio o una string que literal diga none o nulo. 
def es_nulo(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"", "none", "null"}
    if isinstance(value, list):
        return len(value) == 0
    return False

# Funcion para siempre recibir una lista al pasar cualquier valor, si es un null, se devuelve una lista vacia
# si ya es una lista simplemente devuelve lo mismo y si es un solo valor, lo envuelve en una lista.
def hacer_lista(value):
    if es_nulo(value):
        return []
    if isinstance(value, list):
        return value
    return [value]

# retorna un diccionario con la forma que estandarice para manejar la información del doctor, practicamente solo asigna las keys y los valores del diccionario
# y hace una lista a todos los atributos (a excepcion de "sobre mi"), tambien se regulariza la seccion del diccionario de experencia en todo caso no fuera un diccionario
def limpiar_doctor(doctor):
    experiencia = doctor.get("experiencia") or {}
    if not isinstance(experiencia, dict):
        experiencia = {}

    return {
        "nombre_doctor": doctor.get("nombre_doctor"),
        "especialidad": doctor.get("especialidad"),
        "cedula": hacer_lista(doctor.get("cedula")),
        "experiencia": {
            "formacion": hacer_lista(experiencia.get("formacion")),
            "sobre_mi": None if es_nulo(experiencia.get("sobre_mi")) else str(experiencia.get("sobre_mi")).strip(),
            "enfermedades_tratadas": hacer_lista(experiencia.get("enfermedades_tratadas")),
            "lenguajes": hacer_lista(experiencia.get("lenguajes")),
            "enfoques": hacer_lista(experiencia.get("enfoques")),
            "pacientes": hacer_lista(experiencia.get("pacientes")),
            "redes_sociales": hacer_lista(experiencia.get("redes_sociales")),
        },
        "clinicas": hacer_lista(doctor.get("clinicas")),
        "servicios": hacer_lista(doctor.get("servicios")),
        "aseguradoras": hacer_lista(doctor.get("aseguradoras")),
        "opiniones": hacer_lista(doctor.get("opiniones")),
    }

# Recorre todos los doctores y aplica la limpieza de los doctores a cada doctor para devolver el array de todos los diccionarios con la información de los doctores.
def dataset_limpio(doctores):
    resultado = []
    for d in doctores:
        resultado.append(
            limpiar_doctor(d)
        )
    return resultado