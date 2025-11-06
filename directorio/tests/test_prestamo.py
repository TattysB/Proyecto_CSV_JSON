# -*- coding: utf-8 -*-
import os
import json
from datetime import date, timedelta
from directorio import prestamos, gestor_datos2

CARPETA_TEMP = os.path.join(os.getcwd(), "tests", "temp_data")
os.makedirs(CARPETA_TEMP, exist_ok=True)


def crear_json_temporal(nombre, datos):
    """Crea un archivo JSON dentro de tests/temp_data/"""
    ruta = os.path.join(CARPETA_TEMP, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
    return ruta


def eliminar_archivo(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


def test_buscar_en_json_y_csv():
    datos = [{"documento": "123", "nombre": "Tatiana"}]
    archivo = crear_json_temporal("usuarios_busqueda.json", datos)

    resultado = prestamos.buscar_en_json_y_csv(archivo, "documento", "123")
    assert resultado == {"documento": "123", "nombre": "Tatiana"}

    eliminar_archivo(archivo)


def test_realizar_prestamo_correcto():
    archivo_usuarios = crear_json_temporal("usuarios.json", [{"documento": "1", "nombres": "Yeimy", "apellidos": "Bayona"}])
    archivo_libros = crear_json_temporal("libros.json", [{"ISBN": "100", "nombre": "Python Básico", "autor": "Guido", "stock": "2"}])
    archivo_prestamos = crear_json_temporal("prestamos.json", [])

    nuevo = prestamos.realizar_prestamo(
        archivo_prestamos, archivo_usuarios, archivo_libros,
        nuevo_id_usuario="1", nuevo_id_libro="100"
    )

    assert nuevo["estado"] == "prestado"
    libros_actualizados = gestor_datos2.cargar_datos(archivo_libros)
    assert libros_actualizados[0]["stock"] == "1"

    eliminar_archivo(archivo_usuarios)
    eliminar_archivo(archivo_libros)
    eliminar_archivo(archivo_prestamos)


def test_registrar_devolucion():
    prestamos_data = [{"id_prestamo": "1", "id_usuario": "1", "id_libro": "100", "estado": "prestado"}]
    libros_data = [{"ISBN": "100", "stock": "1"}]

    archivo_prestamos = crear_json_temporal("prestamos_dev.json", prestamos_data)
    archivo_libros = crear_json_temporal("libros_dev.json", libros_data)

    resultado = prestamos.registrar_devolucion(archivo_prestamos, archivo_libros, "1")
    assert resultado["estado"] == "devuelto"

    libros_actualizados = gestor_datos2.cargar_datos(archivo_libros)
    assert libros_actualizados[0]["stock"] == "2"

    eliminar_archivo(archivo_prestamos)
    eliminar_archivo(archivo_libros)


def test_listar_prestamos():
    prestamos_data = [{
        "id_prestamo": "1",
        "id_usuario": "1",
        "id_libro": "100",
        "fecha_prestamo": str(date.today()),
        "fecha_devolucion_esperada": str(date.today() - timedelta(days=2)),
        "estado": "prestado"
    }]
    usuarios_data = [{"documento": "1", "nombres": "Yeimy", "apellidos": "Bayona"}]
    libros_data = [{"ISBN": "100", "nombre": "Python Básico"}]

    archivo_prestamos = crear_json_temporal("prestamos_listar.json", prestamos_data)
    archivo_usuarios = crear_json_temporal("usuarios_listar.json", usuarios_data)
    archivo_libros = crear_json_temporal("libros_listar.json", libros_data)

    resultado = prestamos.listar_prestamos(archivo_prestamos, archivo_usuarios, archivo_libros)
    assert len(resultado) == 1
    assert resultado[0]["usuario"] == "Yeimy Bayona"
    assert resultado[0]["libro"] == "Python Básico"

    eliminar_archivo(archivo_prestamos)
    eliminar_archivo(archivo_usuarios)
    eliminar_archivo(archivo_libros)
