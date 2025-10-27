"""
CLIENTE
"""

# -*- coding: utf-8 -*-
"""
Módulo de Lógica de Negocio.

Contiene todas las funciones para gestionar la agenda de usuarios (CRUD).
Este módulo utiliza 'gestor_datos' para la persistencia.
"""

from typing import Any, Dict, List, Optional

import gestor_datos


def generar_id(usuarios: List[Dict[str, Any]]) -> int:
    """
    Genera un nuevo ID autoincremental para un usuario.

    Args:
        usuarios (List[Dict[str, Any]]): La lista actual de usuarios.

    Returns:
        int: El nuevo ID a asignar.
    """
    if not usuarios:
        return 1

    max_id = max(int(ap.get('id', 0)) for ap in usuarios)
    return max_id + 1


def crear_usuario(
        filepath: str,
        documento: int,
        nombres: str,
        apellidos: str,
        email: str,

) -> Optional[Dict[str, Any]]:
    """
    (CREATE) Agrega un nuevo usuario a la agenda.

    Valida que el número de documento no exista antes de agregarlo.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (int): Número de documento del usuario.
        nombres (str): Nombres del usuario.
        apellidos (str): Apellidos del usuario.
        email (str): Dirección de residencia.

    Returns:
        Optional[Dict[str, Any]]: El diccionario del usuario creado o None si ya existía.
    """
    usuarios = gestor_datos.cargar_datos(filepath)
    str_documento = str(documento)

    if any(ap.get('documento') == str_documento for ap in usuarios):
        print(f"\n❌ Error: El documento '{str_documento}' ya se encuentra registrado.")
        return None

    nuevo_id = generar_id(usuarios)

    nuevo_usuario = {
        'id': str(nuevo_id),
        'documento': str_documento,
        'nombres': nombres,
        'apellidos': apellidos,
        'email': email,

    }

    usuarios.append(nuevo_usuario)
    gestor_datos.guardar_datos(filepath, usuarios)
    return nuevo_usuario


def leer_todos_los_usuario(filepath: str) -> List[Dict[str, Any]]:
    """
    (READ) Obtiene la lista completa de usuarios.

    Args:
        filepath (str): Ruta al archivo de datos.

    Returns:
        List[Dict[str, Any]]: La lista de usuarios.
    """
    return gestor_datos.cargar_datos(filepath)


def buscar_usuario_por_documento(filepath: str, documento: str) -> Optional[Dict[str, Any]]:
    """
    Busca un usuario específico por su número de documento.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento a buscar.

    Returns:
        Optional[Dict[str, Any]]: El diccionario del usaurio si se encuentra, de lo contrario None.
    """
    usuarios = gestor_datos.cargar_datos(filepath)
    for usaurio in usuarios:
        if usaurio.get('documento') == documento:
            return usaurio
    return None


def actualizar_usuario(
        filepath: str,
        documento: str,
        datos_nuevos: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    (UPDATE) Modifica los datos de un usuario existente.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento del usuario a actualizar.
        datos_nuevos (Dict[str, Any]): Un diccionario con los campos a actualizar.

    Returns:
        Optional[Dict[str, Any]]: El diccionario del usuario actualizado, o None si no se encontró.
    """
    usuarios = gestor_datos.cargar_datos(filepath)
    usuario_encontrado = None
    indice = -1

    for i, usuario in enumerate(usuarios):
        if usuario.get('documento') == documento:
            usuario_encontrado = usuario
            indice = i
            break

    if usuario_encontrado:
        # Convertimos todos los nuevos valores a string para consistencia
        for key, value in datos_nuevos.items():
            datos_nuevos[key] = str(value)

        usuario_encontrado.update(datos_nuevos)
        usuarios[indice] = usuario_encontrado
        gestor_datos.guardar_datos(filepath, usuarios)
        return usuario_encontrado

    return None


def eliminar_usuario(filepath: str, documento: str) -> bool:
    """
    (DELETE) Elimina un usuario de la agenda.

    Args:
        filepath (str): Ruta al archivo de datos.
        documento (str): El documento del usuario a eliminar.

    Returns:
        bool: True si el usuario fue eliminado, False si no se encontró.
    """
    usuarios = gestor_datos.cargar_datos(filepath)
    usuario_a_eliminar = None

    for usuario in usuarios:
        if usuario.get('documento') == documento:
            usuario_a_eliminar = usuario
            break

    if usuario_a_eliminar:
        usuarios.remove(usuario_a_eliminar)
        gestor_datos.guardar_datos(filepath, usuarios)
        return True

    return False

