# -*- coding: utf-8 -*-
import os
import json
from directorio import usuario


CARPETA_TEMP = os.path.join(os.getcwd(), "tests", "temp_data")
os.makedirs(CARPETA_TEMP, exist_ok=True)


def crear_archivo_temp(nombre="usuarios_temp.json", datos_iniciales=None):
    """Crea un archivo JSON temporal dentro de tests/temp_data/."""
    ruta = os.path.join(CARPETA_TEMP, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos_iniciales or [], f, indent=4, ensure_ascii=False)
    return ruta


def leer_json(filepath):
    """Lee el contenido JSON del archivo."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def eliminar_archivo(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


# --- TESTS ---

def test_crear_usuario_correcto():
    filepath = crear_archivo_temp("usuarios_crear.json")

    nuevo_usuario = usuario.crear_usuario(
        filepath=filepath,
        documento=123,
        nombres="Tatiana",
        apellidos="Bayona",
        email="taty@example.com",
    )

    data = leer_json(filepath)
    assert nuevo_usuario in data
    assert nuevo_usuario["documento"] == "123"

    eliminar_archivo(filepath)


def test_buscar_usuario_por_documento():
    filepath = crear_archivo_temp("usuarios_buscar.json")
    usuario.crear_usuario(filepath, 555, "Laura", "Pérez", "laura@example.com")

    encontrado = usuario.buscar_usuario_por_documento(filepath, "555")

    assert encontrado is not None
    assert encontrado["nombres"] == "Laura"

    eliminar_archivo(filepath)


def test_actualizar_usuario():
    filepath = crear_archivo_temp("usuarios_actualizar.json")
    usuario.crear_usuario(filepath, 777, "Sofía", "Gómez", "sofia@oldmail.com")

    actualizado = usuario.actualizar_usuario(
        filepath, "777", {"email": "sofia@newmail.com"}
    )

    assert actualizado is not None
    assert actualizado["email"] == "sofia@newmail.com"

    eliminar_archivo(filepath)


def test_eliminar_usuario():
    filepath = crear_archivo_temp("usuarios_eliminar.json")
    usuario.crear_usuario(filepath, 999, "Carlos", "Ramírez", "carlos@example.com")

    eliminado = usuario.eliminar_usuario(filepath, "999")

    assert eliminado is True
    data = leer_json(filepath)
    assert not any(u["documento"] == "999" for u in data)

    eliminar_archivo(filepath)
