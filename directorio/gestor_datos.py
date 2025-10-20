# -*- coding: utf-8 -*-
"""
Módulo de Persistencia de Datos.

Responsable de leer y escribir datos en archivos planos (CSV y JSON).
No contiene lógica de negocio, solo operaciones de I/O.
"""

import csv
import json
import os
from typing import Any, Dict, List

# Se define el orden de las columnas para los archivos.
# Se añade 'tipo_documento' como nuevo campo.
CAMPOS = ['id', 'documento', 'nombres', 'apellidos','email']

def inicializar_archivo(filepath: str) -> None:
    """
    Verifica si un archivo de datos existe. Si no, lo crea con las cabeceras.

    Esta función es clave para evitar errores en la primera ejecución del programa.

    Args:
        filepath (str): La ruta completa al archivo de datos (e.g., 'data/aprendices.csv').
    """
    directorio = os.path.dirname(filepath)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio)

    if not os.path.exists(filepath):
        if filepath.endswith('.csv'):
            with open(filepath, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=CAMPOS)
                writer.writeheader()
        elif filepath.endswith('.json'):
            with open(filepath, mode='w', encoding='utf-8') as json_file:
                json.dump([], json_file)

def cargar_datos(filepath: str) -> List[Dict[str, Any]]:
    """
    Carga los datos desde un archivo (CSV o JSON) y los retorna como una lista de diccionarios.

    Args:
        filepath (str): La ruta al archivo de datos.

    Returns:
        List[Dict[str, Any]]: Una lista de diccionarios con los datos de los aprendices.
    """
    inicializar_archivo(filepath)

    try:
        if filepath.endswith('.csv'):
            with open(filepath, mode='r', newline='', encoding='utf-8') as csv_file:
                lector = csv.DictReader(csv_file)
                return list(lector)
        elif filepath.endswith('.json'):
            with open(filepath, mode='r', encoding='utf-8') as json_file:
                datos = json.load(json_file)
                return datos if isinstance(datos, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_datos(filepath: str, datos: List[Dict[str, Any]]) -> None:
    """
    Guarda una lista de diccionarios en un archivo (CSV o JSON), sobrescribiendo el contenido.

    Args:
        filepath (str): La ruta al archivo donde se guardarán los datos.
        datos (List[Dict[str, Any]]): La lista de aprendices a guardar.
    """
    if filepath.endswith('.csv'):
        with open(filepath, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CAMPOS)
            writer.writeheader()
            writer.writerows(datos)
    elif filepath.endswith('.json'):
        with open(filepath, mode='w', encoding='utf-8') as json_file:
            json.dump(datos, json_file, indent=4)

