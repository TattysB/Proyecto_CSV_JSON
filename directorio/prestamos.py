# -*- coding: utf-8 -*-
"""
Módulo de Lógica de Negocio.

Contiene todas las funciones para gestionar la agenda de aprendices (CRUD).
Este módulo utiliza 'gestor_datos' para la persistencia.
"""

from typing import Any, Dict, List, Optional

import gestor_datos


def generar_id(clientes: List[Dict[str, Any]]) -> int:
    """
    Genera un nuevo ID autoincremental para un aprendiz.

    Args:
        clientes (List[Dict[str, Any]]): La lista actual de aprendices.

    Returns:
        int: El nuevo ID a asignar.
    """
    if not clientes:
        return 1
    
    max_id = max(int(ap.get('id', 0)) for ap in clientes)
    return max_id + 1

def crear_cliente(
        filepath: str,
        documento: int,
        nombres: str,
        apellidos: str,
        email: str,

) -> Optional[Dict[str, Any]]:
    """
    (CREATE) Agrega un nuevo aprendiz a la agenda.

    Valida que el número de documento no exista antes de agregarlo.

    Args:
        filepath (str): Ruta al archivo de datos.
        tipo_documento (str): Abreviatura del tipo de documento (ej. 'C.C').
        documento (int): Número de documento del aprendiz.
        nombres (str): Nombres del aprendiz.
        apellidos (str): Apellidos del aprendiz.
        email (str): Dirección de residencia.
        telefono (int): Número de teléfono.
        ficha (int): Número de la ficha del programa.

    Returns:
        Optional[Dict[str, Any]]: El diccionario del aprendiz creado o None si ya existía.
    """
    clientes = gestor_datos.cargar_datos(filepath)
    str_documento = str(documento)

    if any(ap.get('documento') == str_documento for ap in clientes):
        print(f"\n❌ Error: El documento '{str_documento}' ya se encuentra registrado.")
        return None

    nuevo_id = generar_id(clientes)

    nuevo_cliente = {
        'id': str(nuevo_id),
        'documento': str_documento,
        'nombres': nombres,
        'apellidos': apellidos,
        'email': email,

    }

    clientes.append(nuevo_cliente)
    gestor_datos.guardar_datos(filepath, clientes)
    return nuevo_cliente

def leer_todos_los_clientes(filepath: str) -> List[Dict[str, Any]]:
    """
    (READ) Obtiene la lista completa de aprendices.

    Args:
        filepath (str): Ruta al archivo de datos.

    Returns:
        List[Dict[str, Any]]: La lista de aprendices.
    """
    return gestor_datos.cargar_datos(filepath)

def buscar_cliente_por_documento(filepath: str, documento: str) -> Optional[Dict[str, Any]]:
    """
    Busca un cliente específico por su número de documento.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento a buscar.

    Returns:
        Optional[Dict[str, Any]]: El diccionario del cliente si se encuentra, de lo contrario None.
    """
    clientes = gestor_datos.cargar_datos(filepath)
    for cliente in clientes:
        if cliente.get('documento') == documento:
            return cliente
    return None

def actualizar_cliente(
        filepath: str,
        documento: str,
        datos_nuevos: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    (UPDATE) Modifica los datos de un cliente existente.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento del cliente a actualizar.
        datos_nuevos (Dict[str, Any]): Un diccionario con los campos a actualizar.

    Returns:
        Optional[Dict[str, Any]]: El diccionario del cliente actualizado, o None si no se encontró.
    """
    clientes = gestor_datos.cargar_datos(filepath)
    cliente_encontrado = None
    indice = -1

    for i, cliente in enumerate(clientes):
        if cliente.get('documento') == documento:
            cliente_encontrado = cliente
            indice = i
            break


    if cliente_encontrado:
        # Convertimos todos los nuevos valores a string para consistencia
        for key, value in datos_nuevos.items():
            datos_nuevos[key] = str(value)

        cliente_encontrado.update(datos_nuevos)
        clientes[indice] = cliente_encontrado
        gestor_datos.guardar_datos(filepath, clientes)
        return cliente_encontrado

    return None

def eliminar_cliente(filepath: str, documento: str) -> bool:
    """
    (DELETE) Elimina un cliente de la agenda.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento del cliente a eliminar.

    Returns:
        bool: True si el cliente fue eliminado, False si no se encontró.
    """
    clientes = gestor_datos.cargar_datos(filepath)
    cliente_a_eliminar = None

    for cliente in clientes:
        if cliente.get('documento') == documento:
            cliente_a_eliminar = cliente
            break

    if cliente_a_eliminar:
        clientes.remove(cliente_a_eliminar)
        gestor_datos.guardar_datos(filepath, clientes)
        return True

    return False