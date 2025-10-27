# -*- coding: utf-8 -*-
"""
Módulo de Préstamos
-------------------
Se encarga de registrar los préstamos de productos (libros) a clientes.
Guarda los datos en un archivo JSON y CSV.
"""

from datetime import date
import gestor_datos3  # préstamos
import gestor_datos2 # libros
import gestor_datos   # usuarios
import csv
import json
import os
from rich.console import Console

console = Console()



# Obtener la ruta absoluta de la carpeta raíz del proyecto


# ---------------------------------------------------------------------
# 🔍 FUNCIÓN: Buscar registro en JSON y CSV
# ---------------------------------------------------------------------
def buscar_en_json_y_csv(archivo: str, clave: str, valor: str):
    """
    Busca un registro por clave y valor tanto en JSON como en CSV.
    Usa automáticamente el gestor correcto según el archivo.

    """


    console.print(f"[cyan]🔍 Buscando en archivo:[/cyan] {archivo}")

    # Determinar gestor según el tipo de archivo
    if "usuario" in archivo or "cliente" in archivo:
        gestor = gestor_datos
    elif "libro" in archivo or "producto" in archivo:
        gestor = gestor_datos2
    else:
        raise ValueError(f"No se puede determinar el gestor para: {archivo}")


    # 1️⃣ Buscar en JSON
    if os.path.exists(archivo):
        datos_json = gestor.cargar_datos(archivo)
        console.print(f"[blue]📘 Registros JSON cargados:[/blue] {len(datos_json)}")
        for item in datos_json:
            if str(item.get(clave)) == str(valor):
                console.print(f"[green]✅ Encontrado en JSON[/green]: {item}")
                return item
    else:
        console.print(f"[red]⚠️ Archivo JSON no encontrado:[/red] {archivo}")

    # 2️⃣ Buscar en CSV (si existe)
    archivo_csv = archivo.replace(".json", ".csv")
    if os.path.exists(archivo_csv):
        datos_csv = gestor.cargar_datos(archivo_csv)
        console.print(f"[blue]📗 Registros CSV cargados:[/blue] {len(datos_csv)}")
        for item in datos_csv:
            if str(item.get(clave)) == str(valor):
                console.print(f"[green]✅ Encontrado en CSV[/green]: {item}")
                return item
    else:
        console.print(f"[red]⚠️ Archivo CSV no encontrado:[/red] {archivo_csv}")

    console.print(f"[red]❌ No se encontró {valor} en {archivo} ni en {archivo_csv}[/red]")
    return None


# ---------------------------------------------------------------------
# 📚 FUNCIÓN: Registrar préstamo
# ---------------------------------------------------------------------
def realizar_prestamo(archivo_prestamo: str, archivo_usuario: str, archivo_libro: str,
                      nuevo_id_usuario: str, nuevo_id_libro: str):
    """
    Registra un préstamo nuevo si el usuario y el libro existen.
    Guarda el préstamo tanto en JSON como en CSV usando los gestores.
    """
    prestamos=[]
    if os.path.exists(archivo_prestamo):
        prestamos = gestor_datos3.cargar_datos(archivo_prestamo)
        console.print(f"[blue]📘 Préstamos cargados:[/blue] {len(prestamos)}")

    # Verificar si el usuario existe
    usuario_encontrado = buscar_en_json_y_csv(archivo_usuario, "documento", nuevo_id_usuario)
    if not usuario_encontrado:
        console.print("[bold red]❌ El usuario no existe en JSON ni CSV[/bold red]")
        return None

    # Verificar si el libro existe
    libro_encontrado = buscar_en_json_y_csv(archivo_libro, "ISBN", nuevo_id_libro)
    if not libro_encontrado:
        console.print("[bold red]❌ El libro no existe en JSON ni CSV[/bold red]")
        return None

    # Crear el préstamo
    nuevo_prestamo = {
        "id_prestamo": len(prestamos) + 1,
        "id_usuario": nuevo_id_usuario,
        "id_libro": nuevo_id_libro,
        "fecha": str(date.today()),
        "estado": "prestado"
    }

    prestamos.append(nuevo_prestamo)
    gestor_datos3.guardar_datos(archivo_prestamo, prestamos)

    # Guardar también en CSV
    archivo_csv = archivo_prestamo.replace(".json", ".csv")
    with open(archivo_csv, "w", newline="", encoding="utf-8") as f:
        campos = ["id_prestamo", "id_usuario", "id_libro", "fecha", "estado"]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(prestamos)

    console.print("[bold green]✅ Préstamo registrado correctamente[/bold green]")
    return nuevo_prestamo


# ---------------------------------------------------------------------
# 🔄 FUNCIÓN: Registrar devolución
# ---------------------------------------------------------------------
def registrar_devolucion(archivo_prestamo: str, archivo_libros: str, id_prestamo: str):
    """
    Registra la devolución de un producto prestado, cambiando su estado y aumentando el stock.
    """
    prestamos = gestor_datos3.cargar_datos(archivo_prestamo)
    libros = gestor_datos2.cargar_datos(archivo_libros)

    # Buscar el préstamo
    prestamo = next((p for p in prestamos if str(p.get("id_prestamo")) == str(id_prestamo)), None)
    if not prestamo:
        console.print("[bold red]❌ No se encontró el préstamo indicado[/bold red]")
        return None

    if prestamo.get("estado") == "devuelto":
        console.print("[yellow]⚠️ El préstamo ya fue devuelto[/yellow]")
        return None

    # Cambiar estado
    prestamo["estado"] = "devuelto"

    # Aumentar stock del libro devuelto
    id_libro = prestamo.get("id_libro")
    libro_encontrado = next((lb for lb in libros if str(lb.get("ISBN")) == str(id_libro)), None)

    if libro_encontrado:
        try:
            libro_encontrado["stock"] = str(int(libro_encontrado.get("stock", "0")) + 1)
        except ValueError:
            libro_encontrado["stock"] = "1"

        gestor_datos2.guardar_datos(archivo_libros, libros)
        gestor_datos3.guardar_datos(archivo_prestamo, prestamos)

        console.print("[bold green]✅ Devolución registrada correctamente[/bold green]")
        return prestamo
    else:
        console.print("[bold red]❌ No se encontró el libro asociado[/bold red]")
        return None
# ---------------------------------------------------------------------
# 📋 FUNCIÓN: Listar todos los préstamos
# ---------------------------------------------------------------------
def listar_prestamos(archivo_prestamo: str, archivo_usuario: str, archivo_libro: str):
    """
    Retorna una lista con los préstamos registrados, mostrando
    los datos combinados de usuario y libro.
    """

    # Cargar los datos
    prestamos = gestor_datos3.cargar_datos(archivo_prestamo)
    usuarios = gestor_datos.cargar_datos(archivo_usuario)
    libros = gestor_datos2.cargar_datos(archivo_libro)

    if not prestamos:
        return []  # No hay préstamos

    lista_resultado = []

    for prestamo in prestamos:
        # Buscar usuario y libro asociados
        usuario = next((u for u in usuarios if str(u.get("documento")) == str(prestamo.get("id_usuario"))), None)
        libro = next((l for l in libros if str(l.get("ISBN")) == str(prestamo.get("id_libro"))), None)

        # Armar el registro combinado
        registro = {
            "id_prestamo": prestamo.get("id_prestamo"),
            "usuario": usuario.get("nombre") if usuario else "Desconocido",
            "libro": libro.get("titulo") if libro else "Desconocido",
            "fecha": prestamo.get("fecha"),
            "estado": prestamo.get("estado")
        }

        lista_resultado.append(registro)

    return lista_resultado

def listar_devoluciones(archivo_prestamo: str, archivo_usuario: str, archivo_libro: str):
    """
    Retorna una lista de todos los préstamos que ya fueron devueltos,
    mostrando datos combinados de usuario y libro.
    """
    # Cargar todos los préstamos
    prestamos = listar_prestamos(archivo_prestamo, archivo_usuario, archivo_libro)

    # Filtrar solo los que están devueltos
    devoluciones = [p for p in prestamos if p['estado'] == 'devuelto']

    return devoluciones
