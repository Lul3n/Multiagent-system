import json
from pathlib import Path
from limpiar_data import dataset_limpio
from extraer_atributos import extraer_datos_doctor
from puntajes import ( calcular_contexto_dataset, puntaje_confianza, evaluar_doctor,)


ARCHIVO_DATOS = Path("doctor_data.json")

#abre la ruta del json y carga los datos
def cargar_datos():
    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
        return json.load(archivo)

#junta todas las funciones ya hechas e imprime los resultados
def main():
    doctores = cargar_datos()
    doctores = dataset_limpio(doctores)

    filas = []

    for doctor in doctores:
        filas.append({
            "doctor": doctor,
            "caracteristicas": extraer_datos_doctor(doctor),
        })
    contexto = calcular_contexto_dataset(filas)

    clasificacion = []

    for fila in filas:
        puntaje, componentes = evaluar_doctor(
            fila["caracteristicas"],
            contexto
        )

        confianza = puntaje_confianza(
            fila["caracteristicas"]
        )

        clasificacion.append({
            "doctor": fila["doctor"],
            "caracteristicas": fila["caracteristicas"],
            "puntaje": puntaje,
            "confianza": confianza,
            "componentes": componentes,
        })

    clasificacion.sort(key=lambda x: x["puntaje"], reverse=True)

    print("RANKING GENERAL DE LOS MEJORES DOCTORES")
    print(f"Numero de doctores: {len(clasificacion)}")

    for posicion, elemento in enumerate(clasificacion, start=1):
        doctor = elemento["doctor"]
        caracteristicas = elemento["caracteristicas"]
        componentes = elemento["componentes"]
        print(f"\n #{posicion} {doctor['nombre_doctor']}")
        print(f"ESPECIALIDAD: {doctor['especialidad']}")
        print(f"PUNTAJE GENERAL: {elemento['puntaje']:.2f}/100")
        print(f"CONFIANZA: {elemento['confianza']:.2f}/100")

        print("PUNTUACIÓN POR CATEGORIA:")
        for nombre, valor in componentes.items():
            if valor is None:
                print(f"    {nombre}: Sin datos")
            else:
                print(f"    {nombre}: {valor:.2f}")

        print(
            f"    Opiniones: {caracteristicas['numero_calificaciones']}"
            f"\n    Servicios: {caracteristicas['cantidad_servicios']}"
            f"\n    Clínicas: {caracteristicas['cantidad_clinicas']}"
        )


main()