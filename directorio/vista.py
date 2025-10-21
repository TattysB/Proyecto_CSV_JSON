# -*- coding: utf-8 -*-
"""
Módulo Principal - Interfaz de Usuario (UI).

Punto de entrada de la aplicación.
Maneja la interacción con el usuario (menús, entradas, salidas) usando la librería rich.
"""

import os
import prestamos

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

console =Console()

DIRECTORIO_DATOS = 'data'
NOMBRE_ARCHIVO_CSV = 'libros.csv'
NOMBRE_ARCHIVO_CSV_1='usuarios.csv'
NOMBRE_ARCHIVO_JSON = 'prestamos.json'

