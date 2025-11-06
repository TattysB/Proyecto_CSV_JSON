# -*- coding: utf-8 -*-
import os
import json
from directorio import libro, gestor_datos2

CARPETA_TEMP = os.path.join(os.getcwd(), "tests", "temp_data")
os.makedirs(CARPETA_TEMP, exist_ok=True)


def crear_archivo_temp(nombre="libros_temp.json", datos=None):
    ruta = os.path.join(CARPETA_TEMP, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos or [], f, indent=4, ensure_ascii=False)
    return ruta


def eliminar_archivo(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


def test_crear_libro_correcto():
    filepath = crear_archivo_temp("libro_crear.json")

    nuevo_libro = libro.crear_libro(
        filepath, 12345, "Cien años de soledad", "Gabriel García Márquez", 10
    )

    assert nuevo_libro["ISBN"] == "12345"

    libros_guardados = gestor_datos2.cargar_datos(filepath)
    assert libros_guardados[0]["nombre"] == "Cien años de soledad"

    eliminar_archivo(filepath)


def test_buscar_libro_por_isbn():
    filepath = crear_archivo_temp("libro_buscar.json")
    libro.crear_libro(filepath, 111, "El principito", "Antoine de Saint-Exupéry", 5)

    encontrado = libro.buscar_libro_por_isbn(filepath, "111")
    assert encontrado["nombre"] == "El principito"

    eliminar_archivo(filepath)


def test_actualizar_libro():
    filepath = crear_archivo_temp("libro_actualizar.json")
    libro.crear_libro(filepath, 222, "Don Quijote", "Cervantes", 3)

    actualizado = libro.actualizar_libro(filepath, "222", {"stock": 20})
    assert actualizado["stock"] == "20"

    eliminar_archivo(filepath)


def test_eliminar_libro():
    filepath = crear_archivo_temp("libro_eliminar.json")
    libro.crear_libro(filepath, 333, "Hamlet", "Shakespeare", 2)

    resultado = libro.eliminar_libro(filepath, "333")
    assert resultado is True

    eliminar_archivo(filepath)
