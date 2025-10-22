"""
PRODUCTO
"""

# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Optional

import gestor_datos2

def generar_id_prodcuto(productos: List[Dict[str, Any]]) -> int:
    """
    Genera un nuevo ID autoincremental para un aprendiz.

    Args:
        productos (List[Dict[str, Any]]): La lista actual de aprendices.

    Returns:
        int: El nuevo ID a asignar.
    """
    if not productos:
        return 1

    max_id = max(int(ap.get('id', 0)) for ap in productos)
    return max_id + 1


def crear_producto(
        filepath: str,
        id_producto: int,
        nombre: str,
        precio: float,
        stock: int,

) -> Optional[Dict[str, Any]]:
    """
    (CREATE) Agrega un nuevo aprendiz a la agenda.

    Valida que el número de documento no exista antes de agregarlo.

    Args:
        filepath (str): Ruta al archivo de datos.
        id_producto (int): Número de documento del aprendiz.
        nombre (str): Nombres del aprendiz.
        precio (str): Apellidos del aprendiz.
        stock (str): Dirección de residencia.


    Returns:
        Optional[Dict[str, Any]]: El diccionario del aprendiz creado o None si ya existía.
    """
    productos = gestor_datos2.cargar_datos(filepath)
    str_documento = str(id_producto)

    if any(ap.get('documento') == str_documento for ap in productos):
        print(f"\n❌ Error: El documento '{str_documento}' ya se encuentra registrado.")
        return None

    nuevo_id = generar_id_prodcuto(productos)

    nuevo_producto = {
        'id': str(nuevo_id),
        'ISDN': str_documento,
        'nombre': nombre,
        'precio': precio,
        'stock': stock,

    }

    productos.append(nuevo_producto)
    gestor_datos2.guardar_datos(filepath, productos)
    return nuevo_producto


def leer_todos_los_productos(filepath: str) -> List[Dict[str, Any]]:
    """
    (READ) Obtiene la lista completa de aprendices.

    Args:
        filepath (str): Ruta al archivo de datos.

    Returns:
        List[Dict[str, Any]]: La lista de aprendices.
    """
    return gestor_datos2.cargar_datos(filepath)


def buscar_producto_por_isdn(filepath: str, documento: str) -> Optional[Dict[str, Any]]:
    """
    Busca un producto específico por su número de documento.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento a buscar.

    Returns:
        Optional[Dict[str, Any]]: El diccionario del producto si se encuentra, de lo contrario None.
    """
    productos = gestor_datos2.cargar_datos(filepath)
    for producto in productos:
        if producto.get('ISDN') == documento:
            return producto
    return None


def actualizar_producto(
        filepath: str,
        documento: str,
        datos_nuevos: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    (UPDATE) Modifica los datos de un producto existente.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento del producto a actualizar.
        datos_nuevos (Dict[str, Any]): Un diccionario con los campos a actualizar.

    Returns:
        Optional[Dict[str, Any]]: El diccionario del producto actualizado, o None si no se encontró.
    """

    productos = gestor_datos2.cargar_datos(filepath)
    producto_encontrado = None
    indice = -1

    for i, producto in enumerate(productos):
        if producto.get('ISDN') == documento:
            producto_encontrado = producto
            indice = i
            break

    if producto_encontrado:
        # Convertimos todos los nuevos valores a string para consistencia
        for key, value in datos_nuevos.items():
            datos_nuevos[key] = str(value)

        producto_encontrado.update(datos_nuevos)
        productos[indice] = producto_encontrado
        gestor_datos2.guardar_datos(filepath, productos)
        return producto_encontrado

    return None


def eliminar_producto(filepath: str, documento: str) -> bool:
    """
    (DELETE) Elimina un producto de la agenda.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento del producto a eliminar.

    Returns:
        bool: True si el producto fue eliminado, False si no se encontró.
    """
    productos = gestor_datos2.cargar_datos(filepath)
    producto_a_eliminar = None

    for producto in productos:
        if producto.get('ISDN') == documento:
            producto_a_eliminar = producto
            break

    if producto_a_eliminar:
        productos.remove(producto_a_eliminar)
        gestor_datos2.guardar_datos(filepath, productos)
        return True

    return False