import math
#Estos son los pesos de cada subseccion en la formula, la verdad son estimados asi que se pueden modificar facil desde aqui si es que los de aviada nos dicen algo
PESOS = {
    "reputacion": 0.45,
    "perfil_profesional": 0.25,
    "servicios": 0.15,
    "accesibilidad": 0.10,
    "accesibilidad_economica": 0.05,
}

#Simplemente limita el resultado a que este en un rango de 0 a 100, tecnicamente no deberia de sobrepasar los limites de igual manera
def acotar(valor, minimo=0.0, maximo=100.0):
    return max(minimo, min(maximo, valor))

# Consigue la posición de un valor respecto a los demas (el rango percentil), se ordenan los valores y determina
# a que porcentaje del grupo supera o es igual la cifra actual.
def rango_percentil(valor, valores):
    if valor is None or not valores:
        return None
    ordenados = sorted(valores)
    if len(ordenados) == 1:
        return 50.0

    menores = sum(v < valor for v in ordenados)
    iguales = sum(v == valor for v in ordenados)

    posicion = (menores + 0.5 * iguales) / len(ordenados)
    return acotar(posicion * 100)

# Hace una optimizacion por medio de una formula logaritmica a los datos antes de calcular los percentiles, 
# sirve mucho particularmente en el calculo en base a reputacion, porque hay muchos medicos con 0 reviews
# y los demas pasan de 0 a 10 reviews, pasa algo similar con los servicios, entonces esto ayuda mucho a 
# suavizar el impacto de esos outliers al resultado final, practicamente "apachurras" los maximos y minimos de la funcion
# por ponerlo de forma simple.
def percentil_logaritmico(valor, valores):
    if valor is None or not valores:
        return None
    transformados = [math.log1p(v) for v in valores]
    return rango_percentil(math.log1p(valor), transformados)

#Esta funcion es mas que nada para las reviews, como hay medicos que pueden llegar a tener 1 review de 1 estrella
#el simplemente asignar un 100 de calificacion porque solo tiene una review pues no es realista, lo unico que se hace
# en esta funcion es ponderar la calificación real con la calificacion global promedio del data set entero, todos los
# este ajuste solo afecta a los doctores con pocas reviews, no afecta practicamente la calificación de los doctores con
# muchas reviews, esto es practicamente un algoritmo bayesiano para evitar resultados poco precisos a falta de reviews.
def ajuste_por_promedio_global(suma_estrellas, numero_calificaciones, promedio_global, peso_previo=5):
    if numero_calificaciones == 0:
        return None
    return (suma_estrellas + promedio_global * peso_previo) / (numero_calificaciones + peso_previo)

# calcula el promedio de estrellas de todo el data set y extrae las listas de valores de cada campo. Ademas del promedio
# global de cada estrella tambien saca otros datos generales que se necesitan despues, como el numero de calificaciones global.
def calcular_contexto_dataset(filas_caracteristicas):
    campos = [
        "cantidad_servicios",
        "servicios_con_precio",
        "numero_titulos",
        "enfermedades_tratadas",
        "numero_enfoques",
        "cantidad_cedulas",
        "cantidad_clinicas",
        "cantidad_aseguradoras",
        "cantidad_idiomas",
        "cantidad_tipos_paciente",
        "precio_promedio",
    ]

    contexto = {}

    suma_estrellas_global = 0
    numero_calificaciones_global = 0

    for fila in filas_caracteristicas:
        suma_estrellas_global += fila["caracteristicas"]["suma_estrellas"]
        numero_calificaciones_global += fila["caracteristicas"]["numero_calificaciones"]

    if numero_calificaciones_global > 0:
        promedio_global = (
            suma_estrellas_global /
            numero_calificaciones_global
        )
    else:
        promedio_global = 0

    contexto["promedio_global"] = promedio_global

    for campo in campos:
        valores = [
            fila["caracteristicas"][campo]
            for fila in filas_caracteristicas
            if fila["caracteristicas"].get(campo) is not None
        ]

        contexto[campo] = valores

    contexto["filas"] = filas_caracteristicas

    return contexto

#Es lo que se encarga del puntaje general, evaluando las areas de reputacion, perfil personal, servicios
#accesibilidad y accesibilidad economica, haciendo uso de los rangos percentiles y los percentiles 
# logaritmicos dependiendo de la variabilidad de los datos (por ejemplo en la seccion de accesibilidad economica
# donde practicamente si se usa el rango percentil directo, son datos directos que no se tiene que suavizar), 
# aparte de eso, la funcion ponderiza las dimensiones disponibles basandose en los pesos de cada seccion y devuelve
# la calificacion
def evaluar_doctor(caracteristicas, contexto):
    calificacion_ajustada = ajuste_por_promedio_global(
        caracteristicas["suma_estrellas"],
        caracteristicas["numero_calificaciones"],
        contexto["promedio_global"]
    )

    if calificacion_ajustada is None:
        reputacion = None
    else:
        puntaje_calificacion = ((calificacion_ajustada - 1) / 4) * 100
        puntaje_opiniones = percentil_logaritmico(
            caracteristicas["numero_calificaciones"],
            [f["caracteristicas"]["numero_calificaciones"] for f in contexto["filas"]]
        )
        reputacion = (puntaje_calificacion * 0.75 + puntaje_opiniones * 0.25)

    titulos = percentil_logaritmico(caracteristicas["numero_titulos"], contexto["numero_titulos"])
    enfermedades = percentil_logaritmico(caracteristicas["enfermedades_tratadas"], contexto["enfermedades_tratadas"])
    enfoques = percentil_logaritmico(caracteristicas["numero_enfoques"], contexto["numero_enfoques"])
    cedulas = percentil_logaritmico(caracteristicas["cantidad_cedulas"], contexto["cantidad_cedulas"])

    partes_profesionales = [(titulos, 0.35), (enfermedades, 0.30), (enfoques, 0.25), (cedulas, 0.10)]

    perfil_profesional = sum(puntaje * peso for puntaje, peso in partes_profesionales if puntaje is not None)
    servicios = percentil_logaritmico(caracteristicas["cantidad_servicios"], contexto["cantidad_servicios"])
    servicios_con_precio = percentil_logaritmico(caracteristicas["servicios_con_precio"], contexto["servicios_con_precio"])

    puntaje_servicios = (servicios * 0.75 + servicios_con_precio * 0.25)

    clinicas = percentil_logaritmico(caracteristicas["cantidad_clinicas"], contexto["cantidad_clinicas"])
    aseguradoras = percentil_logaritmico(caracteristicas["cantidad_aseguradoras"], contexto["cantidad_aseguradoras"])
    accesibilidad = (clinicas * 0.60 + aseguradoras * 0.40)

    if caracteristicas["precio_promedio"] is not None:
        posicion_precio = rango_percentil(caracteristicas["precio_promedio"], contexto["precio_promedio"])
        accesibilidad_economica = 100 - posicion_precio
    else:
        accesibilidad_economica = None

    componentes = {
        "reputacion": reputacion,
        "perfil_profesional": perfil_profesional,
        "servicios": puntaje_servicios,
        "accesibilidad": accesibilidad,
        "accesibilidad_economica": accesibilidad_economica,
    }

    disponibles = {clave: valor for clave, valor in componentes.items() if valor is not None}
    peso_total = sum(PESOS[k] for k in disponibles)

    puntaje_final = sum(disponibles[k] * PESOS[k] for k in disponibles) / peso_total
    return acotar(puntaje_final), componentes

# Mide que tan confiable es la calificacion de un doctor en funcion de cuantos datos tenia en 
# las secciones mas variables, en este caso la confianza se mide en un 70% en base a cuantas 
#opiniones tenia (Volumen de opiniones) y el otro 30% lo mide en cuantos campos completos tenia en 
# los campos evaluables listados (por ejemplo, el doctor es mejor en cuanto confianza si ha llenado
# todas las secciones en su perfil)
def puntaje_confianza(caracteristicas):
    confianza_opiniones = 100 * (1 - math.exp(-caracteristicas["numero_calificaciones"] / 10))
    campos_evaluables = [
        "numero_titulos",
        "enfermedades_tratadas",
        "numero_enfoques",
        "cantidad_servicios",
        "cantidad_clinicas",
        "cantidad_aseguradoras",
        "cantidad_idiomas",
    ]

    campos_completos = sum(1 for campo in campos_evaluables if caracteristicas[campo] > 0)

    completitud = (campos_completos / len(campos_evaluables)) * 100

    return acotar(confianza_opiniones * 0.70 + completitud * 0.30)