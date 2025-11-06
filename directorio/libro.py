# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Optional

import gestor_datos2

def generar_id_prodcuto(libros: List[Dict[str, Any]]) -> int:
    """
    Genera un nuevo ID autoincremental para un usuario.

    Args:
        libros (List[Dict[str, Any]]): La lista actual de los libros.

    Returns:
        int: El nuevo ID a asignar.
    """
    if not libros:
        return 1

    max_id = max(int(ap.get('id', 0)) for ap in libros)
    return max_id + 1


def crear_libro(
        filepath: str,
        ISBN: int,
        nombre: str,
        autor: str,
        stock: int,

) -> Optional[Dict[str, Any]]:
    """
    (CREATE) Agrega un nuevo libro a la agenda.

    Valida que el número de documento no exista antes de agregarlo.

    Args:
        filepath (str): Ruta al archivo de datos.

        ISBN (str) : código del libro
        nombre (str): Nombres del libro.
        autor (str): Autor del libro.
        stock (str): Dirección de residencia.


    Returns:
        Optional[Dict[str, Any]]: El diccionario del libro creado o None si ya existía.
    """
    libros = gestor_datos2.cargar_datos(filepath)
    str_documento = str(ISBN)

    if any(ap.get('documento') == str_documento for ap in libros):
        print(f"\n❌ Error: El documento '{str_documento}' ya se encuentra registrado.")
        return None

    nuevo_id = generar_id_prodcuto(libros)

    nuevo_libro = {
        'id': str(nuevo_id),
        'ISBN': str_documento,
        'nombre': nombre,
        'autor': autor,
        'stock': stock,

    }

    libros.append(nuevo_libro)
    gestor_datos2.guardar_datos(filepath, libros)
    return nuevo_libro


def leer_todos_los_libros(filepath: str) -> List[Dict[str, Any]]:
    """
    (READ) Obtiene la lista completa de los libros.

    Args:
        filepath (str): Ruta al archivo de datos.

    Returns:
        List[Dict[str, Any]]: La lista de los libros.
    """
    return gestor_datos2.cargar_datos(filepath)


def buscar_libro_por_isbn(filepath: str, documento: str) -> Optional[Dict[str, Any]]:
    """
    Busca un libro específico por su número de documento.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento a buscar.

    Returns:
        Optional[Dict[str, Any]]: El diccionario del libro si se encuentra, de lo contrario None.
    """
    libros = gestor_datos2.cargar_datos(filepath)
    for libro in libros:
        if libro.get('ISBN') == documento:
            return libro
    return None



def actualizar_libro(
        filepath: str,
        documento: str,
        datos_nuevos: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    (UPDATE) Modifica los datos de un libro existente.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento del libro a actualizar.
        datos_nuevos (Dict[str, Any]): Un diccionario con los campos a actualizar.

    Returns:
        Optional[Dict[str, Any]]: El diccionario del libro actualizado, o None si no se encontró.
    """

    libros = gestor_datos2.cargar_datos(filepath)
    libro_encontrado = None
    indice = -1

    for i, libro in enumerate(libros):
        if libro.get('ISBN') == documento:
            libro_encontrado = libro
            indice = i
            break

    if libro_encontrado:
        # Convertimos todos los nuevos valores a string para consistencia
        for key, value in datos_nuevos.items():
            datos_nuevos[key] = str(value)

        libro_encontrado.update(datos_nuevos)
        libros[indice] = libro_encontrado
        gestor_datos2.guardar_datos(filepath, libros)
        return libro_encontrado

    return None


def eliminar_libro(filepath: str, documento: str) -> bool:
    """
    (DELETE) Elimina un libro de la agenda.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento del libro a eliminar.

    Returns:
        bool: True si el libro fue eliminado, False si no se encontró.
    """
    libros = gestor_datos2.cargar_datos(filepath)
    libro_a_eliminar = None

    for libro in libros:
        if libro.get('ISBN') == documento:
            libro_a_eliminar = libro
            break

    if libro_a_eliminar:
        libros.remove(libro_a_eliminar)
        gestor_datos2.guardar_datos(filepath, libros)
        return True

    return False