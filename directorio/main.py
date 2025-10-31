# -*- coding: utf-8 -*-
"""
Módulo Principal - Interfaz de Usuario (UI).

Punto de entrada de la aplicación.
Maneja la interacción con el usuario (menús, entradas, salidas) usando la librería rich.
"""
import os

import usuario  # Importamos nuestro módulo de lógica de negocio
import libro
import prestamos

# --- Importaciones de la librería Rich ---
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text
from rich import box

# from Proyecto_CSV_JSON.directorio.prestamos import realizar_prestamo

# --- Inicialización de la Consola de Rich ---
console = Console()


# Ruta base (donde está este archivo main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carpeta de datos dentro del directorio
DIRECTORIO_DATOS = os.path.join(BASE_DIR, "data")

# Crear carpeta data si no existe
os.makedirs(DIRECTORIO_DATOS, exist_ok=True)

# Archivos dentro de esa carpeta
ARCHIVO_USUARIOS_JSON = os.path.join(DIRECTORIO_DATOS, "usuario.json")
ARCHIVO_USUARIOS_CSV = os.path.join(DIRECTORIO_DATOS, "usuario.csv")
ARCHIVO_LIBROS_JSON = os.path.join(DIRECTORIO_DATOS, "libro.json")
ARCHIVO_LIBROS_CSV = os.path.join(DIRECTORIO_DATOS, "libro.csv")
ARCHIVO_PRESTAMOS_JSON = os.path.join(DIRECTORIO_DATOS, "prestamo.json")
ARCHIVO_PRESTAMOS_CSV = os.path.join(DIRECTORIO_DATOS, "prestamo.csv")



# --- USUARIOS ---
def menu_crear_usuario(filepath: str):
    """Maneja la lógica para registrar un nuevo aprendiz."""
    console.print(Panel.fit("[bold cyan]📝 Registrar Nuevo Usuario[/bold cyan]"))

    documento = IntPrompt.ask("Número de Documento")
    nombres = Prompt.ask("Nombres")
    apellidos = Prompt.ask("Apellidos")
    email = Prompt.ask("Email")

    usuario_creado = usuario.crear_usuario(
        filepath, documento, nombres, apellidos, email
    )

    if usuario_creado:
        console.print(Panel(f"✅ ¡Usuario registrado con éxito!\n   ID Asignado: [bold yellow]{usuario_creado['id']}[/bold yellow]",
                            border_style="green", title="Éxito"))
    else:
        console.print(Panel("⚠️ No se pudo registrar al usuario. Verifique los datos.",
                            border_style="red", title="Error"))

def menu_leer_usuario(filepath: str):
    """Maneja la lógica para mostrar todos los usuarios en una tabla."""
    console.print(Panel.fit("[bold cyan]👥 Lista de usuarios[/bold cyan]"))
    usuarios = usuario.leer_todos_los_usuario(filepath)

    if not usuarios:
        console.print("[yellow]No hay usuarios registrados.[/yellow]")
        return

    # Creamos la tabla
    tabla = Table(title="Usuarios Registrados", border_style="blue", show_header=True, header_style="bold magenta")
    tabla.add_column("ID", style="dim", width=5)
    tabla.add_column("Documento", justify="right")
    tabla.add_column("Nombre Completo")
    tabla.add_column("email", justify="right")

    # Ordenamos por Ficha y luego por ID
    usuarios_ordenados = sorted(usuarios, key=lambda x: (int(x['documento']), int(x['id'])))

    for ap in usuarios_ordenados:

        tabla.add_row(
            ap['id'],
            ap['documento'],
            f"{ap['nombres']} {ap['apellidos']}",
            ap['email']
        )

    console.print(tabla)

def menu_actualizar_usuario(filepath: str):
    """Maneja la lógica para actualizar un usuario."""
    console.print(Panel.fit("[bold cyan]✏️ Actualizar Datos del Usuario[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el Documento del usuario a actualizar")

    usuario_actual = usuario.buscar_usuario_por_documento(filepath, str(documento))
    if not usuario_actual:
        console.print("\n[bold red]❌ No se encontró ningún usuario con ese documento.[/bold red]")
        return

    console.print("\nDatos actuales. Presione Enter para no modificar un campo.")
    datos_nuevos = {}

    nombres = Prompt.ask(f"Nombres ({usuario_actual['nombres']})", default=usuario_actual['nombres'])
    if nombres != usuario_actual['nombres']:
        datos_nuevos['nombres'] = nombres

    apellidos = Prompt.ask(f"Apellidos ({usuario_actual['apellidos']})", default=usuario_actual['apellidos'])
    if apellidos != usuario_actual['apellidos']:
        datos_nuevos['apellidos'] = apellidos

    email = Prompt.ask(f"Email ({usuario_actual['email']})", default=(usuario_actual['email']))
    if email != (usuario_actual['email']):
        datos_nuevos['email'] = email

    if not datos_nuevos:
        console.print("\n[yellow]No se modificó ningún dato.[/yellow]")
        return

    usuario_actualizado = usuario.actualizar_usuario(filepath, str(documento), datos_nuevos)
    if usuario_actualizado:
        console.print(Panel("✅ ¡Datos del usuario actualizados con éxito!", border_style="green", title="Éxito"))
    else:
        console.print(Panel("❌ Ocurrió un error al actualizar.", border_style="red", title="Error"))

def menu_eliminar_usuario(filepath: str):
    """Maneja la lógica para eliminar un usuario."""
    console.print(Panel.fit("[bold cyan]🗑️ Eliminar Usuario[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el Documento del usuario a eliminar")

    usuarios = usuario.buscar_usuario_por_documento(filepath, str(documento))
    if not usuarios:
        console.print("\n[bold red]❌ No se encontró ningún usuario con ese documento.[/bold red]")
        return

    confirmacion = Confirm.ask(
        f"¿Está seguro de que desea eliminar a [bold]{usuarios['nombres']} {usuarios['apellidos']}[/bold]?",
        default=False
    )

    if confirmacion:
        if usuario.eliminar_usuario(filepath, str(documento)):
            console.print(Panel("✅ ¡Usuario eliminado con éxito!", border_style="green", title="Éxito"))
        else:
            console.print(Panel("❌ Ocurrió un error al eliminar.", border_style="red", title="Error"))
    else:
        console.print("\n[yellow]Operación cancelada.[/yellow]")

def elegir_almacenamiento() -> str:
    """Pregunta al usuario qué formato de archivo desea usar y construye la ruta."""
    console.print(Panel.fit("[bold cyan]⚙️ Configuración de Almacenamiento[/bold cyan]"))

    prompt_texto = (
        "¿Dónde desea almacenar los datos?\n"
        "[bold yellow]1[/bold yellow]. CSV (Archivo de texto plano)\n"
        "[bold yellow]2[/bold yellow]. JSON (Formato más estructurado)"
    )
    console.print(prompt_texto)

    opcion = Prompt.ask(
        "Opción",
        choices=["1", "2"],
        default="2",
        show_choices=False
    )
    if opcion == '1':
        return os.path.join(DIRECTORIO_DATOS, ARCHIVO_USUARIOS_JSON)
    else:
        return os.path.join(DIRECTORIO_DATOS, ARCHIVO_USUARIOS_CSV)

# --- LIBRO ---

def menu_crear_libro(filepath: str):
    """Maneja la lógica para registrar un nuevo libro."""
    console.print(Panel.fit("[bold cyan]📝 Registrar Nuevo Libro[/bold cyan]"))

    id_libro = IntPrompt.ask("ISBN")
    nombre = Prompt.ask("Nombre")
    autor = Prompt.ask("Autor")
    stock = IntPrompt.ask("Stock")

    libro_creado = libro.crear_libro(
        filepath, id_libro, nombre, autor, stock
    )

    if libro_creado:
        console.print(Panel(
            f"✅ ¡Libro registrado con éxito!\n   ID Asignado: [bold yellow]{libro_creado['id']}[/bold yellow]",
            border_style="green", title="Éxito"))
    else:
        console.print(Panel("⚠️ No se pudo registrar el libro. Verifique los datos.",
                            border_style="red", title="Error"))

def menu_leer_libros(filepath: str):
    """Maneja la lógica para mostrar todos los libros ."""
    console.print(Panel.fit("[bold cyan]👥 Lista de libros[/bold cyan]"))
    libros = libro.leer_todos_los_libros(filepath)

    if not libros:
        console.print("[yellow]No hay libros registrados.[/yellow]")
        return

    # Creamos la tabla
    tabla = Table(title="Libros Registrados", border_style="blue", show_header=True, header_style="bold magenta")
    tabla.add_column("ID", style="dim", width=5)
    tabla.add_column("ISBN", justify="right")
    tabla.add_column("nombre")
    tabla.add_column("autor")
    tabla.add_column("stock", justify="right")

    # Ordenamos por Ficha y luego por ID
    libros_ordenados = sorted(libros, key=lambda x: (int(x['ISBN']), int(x['id'])))

    for ap in libros_ordenados:

        tabla.add_row(
            str(ap['id']),
            str(ap['ISBN']),
            str(ap['nombre']),
            str(ap['autor']),
            str(ap['stock']),
        )

    console.print(tabla)

def menu_actualizar_libro(filepath: str):
    """Maneja la lógica para actualizar un libro."""
    console.print(Panel.fit("[bold cyan]✏️ Actualizar Datos del Libro[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el ISBN del libro a actualizar")

    libro_actual = libro.buscar_libro_por_isbn(filepath, str(documento))
    if not libro_actual:
        console.print("\n[bold red]❌ No se encontró ningún libro con ese ISBN.[/bold red]")
        return

    console.print("\nDatos actuales. Presione Enter para no modificar un campo.")
    datos_nuevos = {}

    nombre = Prompt.ask(f"Nombre ({libro_actual['nombre']})", default=libro_actual['nombre'])
    if nombre != libro_actual['nombre']:
        datos_nuevos['nombre'] = nombre

    autor = Prompt.ask(f"Autor ({libro_actual['autor']})", default=libro_actual['autor'])
    if autor != libro_actual['autor']:
        datos_nuevos['autor'] = autor

    stock = IntPrompt.ask(f"Stock ({libro_actual['stock']})", default=(libro_actual['stock']))
    if stock != (libro_actual['stock']):
        datos_nuevos['stock'] = stock

    if not datos_nuevos:
        console.print("\n[yellow]No se modificó ningún dato.[/yellow]")
        return

    libro_actualizado = libro.actualizar_libro(filepath, str(documento), datos_nuevos)
    if libro_actualizado:
        console.print(Panel("✅ ¡Datos del libro actualizados con éxito!", border_style="green", title="Éxito"))
    else:
        console.print(Panel("❌ Ocurrió un error al actualizar.", border_style="red", title="Error"))

def menu_eliminar_libro(filepath: str):
    """Maneja la lógica para eliminar un libro."""
    console.print(Panel.fit("[bold cyan]🗑️ Eliminar Libro[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el ISBN del libro a eliminar")

    libros = libro.buscar_libro_por_isbn(filepath, str(documento))
    if not libros:
        console.print("\n[bold red]❌ No se encontró ningún libro con ese ISBN.[/bold red]")
        return

    confirmacion = Confirm.ask(
        f"¿Está seguro de que desea eliminar a [bold]{libros['nombre']} [/bold]?",
        default=False
    )

    if confirmacion:
        if libro.eliminar_libro(filepath, str(documento)):
            console.print(Panel("✅ ¡Libro eliminado con éxito!", border_style="green", title="Éxito"))
        else:
            console.print(Panel("❌ Ocurrió un error al eliminar.", border_style="red", title="Error"))
    else:
        console.print("\n[yellow]Operación cancelada.[/yellow]")

def elegir_almacenamiento2() -> str:
    """Pregunta al usuario qué formato de archivo desea usar y construye la ruta."""
    console.print(Panel.fit("[bold cyan]⚙️ Configuración de Almacenamiento[/bold cyan]"))

    prompt_texto = (
        "¿Dónde desea almacenar los datos?\n"
        "[bold yellow]1[/bold yellow]. CSV (Archivo de texto plano)\n"
        "[bold yellow]2[/bold yellow]. JSON (Formato más estructurado)"
    )
    console.print(prompt_texto)

    opcion = Prompt.ask(
        "Opción",
        choices=["1", "2"],
        default="2",
        show_choices=False
    )
    if opcion == '1':
        return os.path.join(DIRECTORIO_DATOS, ARCHIVO_LIBROS_JSON)
    else:
        return os.path.join(DIRECTORIO_DATOS, ARCHIVO_LIBROS_CSV)


# ----PRÉSTAMO----


def menu_crear_prestamo(filepath: str):
    """Maneja la lógica para registrar un nuevo préstamo"""
    console.print(Panel.fit("[bold cyan]📝 Registrar nuevo préstamo[/bold cyan]"))

    id_usuario = Prompt.ask("ID del usuario")
    id_libro = Prompt.ask("ID del libro")

    prestamo_creado = prestamos.realizar_prestamo(
        ARCHIVO_PRESTAMOS_JSON, # Archivos de préstamos
        ARCHIVO_USUARIOS_JSON, # Usuarios
        ARCHIVO_LIBROS_JSON,  #Libros
        id_usuario,
        id_libro
    )

    if prestamo_creado:
        console.print(Panel.fit(
            f"✅ ¡Préstamo registrado con éxito!\nID Asignado: [bold yellow]{prestamo_creado['id_prestamo']}[/bold yellow]",
            border_style="green", title="Éxito"
        ))
    else:
        console.print(
            Panel.fit(
                "⚠️  No se pudo registrar el préstamo. Verifique los datos.",
                border_style="red",
                title="Error",
            )
        )


def menu_registrar_devolucion(archivo_prestamo: str, archivo_libros: str):
    """Maneja la lógica para registrar la devolución"""
    console.print(Panel.fit("[bold cyan]📦 Registrar devolución[/bold cyan]"))

    id_prestamo = Prompt.ask("id_prestamo")

    devolucion_creado = prestamos.registrar_devolucion(archivo_prestamo, archivo_libros, id_prestamo)

    if devolucion_creado:
        console.print(
            Panel.fit(
                f"\n✅ ¡Devolución registrada correctamente!\n ID Asignado: [bold yellow]{devolucion_creado['id_prestamo']}[/bold yellow]",
                border_style="green",
                title="Éxito",
            )
        )
    else:
        console.print(
            Panel.fit(
                "\n❌ No se encontró el préstamo o ya fue devuelto",
                border_style="red",
                title="Error",
            )
        )


def menu_listar_prestamo(filepath: str):
    """Maneja la lógica para mostrar todos los préstamos."""

    console.print(Panel.fit("[bold cyan]👥 Lista de Préstamos[/bold cyan]"))

    archivo_prestamo = os.path.join("directorio", "data", "prestamo.json")
    archivo_usuario = os.path.join("directorio", "data", "usuario.json")
    archivo_libro = os.path.join("directorio", "data", "libro.json")
    # Llamar a la función que obtiene los préstamos registrados
    prestamos_registrados = prestamos.listar_prestamos(archivo_prestamo, archivo_usuario, archivo_libro)

    if not prestamos_registrados:
        console.print("[yellow]⚠️ No hay préstamos registrados.[/yellow]")
        return
    tabla = Table(
        title="📝 Lista de Préstamos Registrados",
        show_lines=True,
        box=box.DOUBLE_EDGE,
        header_style="bold white on dark_blue",
    )
    tabla.add_column("ID Préstamo", justify="center", style="cyan", no_wrap=True)
    tabla.add_column("Usuario", justify="left", style="magenta")
    tabla.add_column("Libro", justify="left", style="blue")
    tabla.add_column("Fecha préstamo", justify="center", style="green")
    tabla.add_column("Fecha devolución esperada", justify="center", style="bright_cyan")
    tabla.add_column("Estado", justify="center", style="bold yellow")

    # Agregar filas a la tabla
    for p in prestamos_registrados:
        estado = p["estado"]

        if estado == "devuelto":
            color_estado = "[green]Devuelto[/green]"
        elif estado == "atrasado":
            color_estado = "[red bold]Atrasado[/red bold]"
        else:
            color_estado = "[yellow]Prestado[/yellow]"

        tabla.add_row(
            str(p["id_prestamo"]),
            p["usuario"],
            p["libro"],
            p["fecha_prestamo"],
            p.get("fecha_devolucion_esperada", "N/A"),
            color_estado,
        )

    console.print(tabla)

def menu_listar_devoluciones_prestamos():
    """Muestra todos los préstamos devueltos en una tabla."""
    console.print(Panel.fit("[bold cyan]📦 Lista de Devoluciones[/bold cyan]"))

    archivo_prestamo = os.path.join("directorio", "data", "prestamo.json")
    archivo_usuario = os.path.join("directorio", "data", "usuario.json")
    archivo_libro = os.path.join("directorio", "data", "libro.json")

    devoluciones = prestamos.listar_devoluciones(archivo_prestamo, archivo_usuario, archivo_libro)

    if not devoluciones:
        console.print("[yellow]⚠️ No hay devoluciones registradas.[/yellow]")
        return

    tabla = Table(
        title="📦🔙 Lista de Devoluciones Registradas",
        show_lines=True,
        box=box.DOUBLE_EDGE,
    )

    tabla.add_column("ID Préstamo", justify="center", style="cyan")
    tabla.add_column("Usuario", justify="left", style="magenta")
    tabla.add_column("Libro", justify="left", style="blue")
    tabla.add_column("Fecha préstamo", justify="center", style="green")
    tabla.add_column("Fecha devolución esperada", justify="center", style="bright_cyan")
    tabla.add_column("Estado", justify="center", style="bold yellow")

    for d in devoluciones:
        estado = d.get("estado","prestado")

        # Asignar colores según el estado
        if estado == "devuelto":
            color_estado = "[green]Devuelto[/green]"
        elif estado == "atrasado":
            color_estado = "[red bold]Atrasado[/red bold]"
        else:
            color_estado = "[yellow]Prestado[/yellow]"

        tabla.add_row(
            str(d['id_prestamo']),
            d['usuario'],
            d['libro'],
            d['fecha_prestamo'],
            d.get('fecha_devolucion_esperada', "N/A"),
            color_estado,
        )

    console.print(tabla)


def elegir_almacenamiento3()->str:
    """Pregunta al usuario qué formato de archivo desea usar y construye la ruta."""
    console.print(Panel.fit("[bold cyan]⚙️ Configuración de Almacenamiento[/bold cyan]"))

    prompt_texto = (
        "¿Dónde desea almacenar los datos?\n"
        "[bold yellow]1[/bold yellow]. CSV (Archivo de texto plano)\n"
        "[bold yellow]2[/bold yellow]. JSON (Formato más estructurado)"
    )
    console.print(prompt_texto)

    opcion = Prompt.ask(
        "Opción",
        choices=["1", "2"],
        default="2",
        show_choices=False
    )
    if opcion == '1':
        return os.path.join(DIRECTORIO_DATOS,ARCHIVO_PRESTAMOS_JSON)
    else:
        return os.path.join(DIRECTORIO_DATOS,ARCHIVO_PRESTAMOS_CSV)


# --- LISTAS DE OPCIONES ---


def menu_usuarios():
    """Imprime el menú principal en la consola usando un Panel de Rich."""
    menu_c = (
        "[bold yellow]1.[/bold yellow]✍️👤  Registrar un nuevo usuario \n"
        "[bold yellow]2.[/bold yellow]👁️👥  Ver todos los usuarios \n"
        "[bold yellow]3.[/bold yellow]🔄👤  Actualizar datos de un usuario \n"
        "[bold yellow]4.[/bold yellow]🗑️👤  Eliminar un usuario \n"
        "[bold red]5.[/bold red]🚪  Volver al menú principal"
    )
    console.print(
        Panel(
            menu_c,
            title="[bold]🧑‍🤝‍🧑  MENÚ DE USUARIOS[/bold]",
            subtitle="Seleccione una opción",
            border_style="green",
        )
    )


def menu_libros():
    menu_p = (
        "[bold yellow]1.[/bold yellow]➕📖  Registrar un nuevo libro\n"
        "[bold yellow]2.[/bold yellow]📖🔍  Ver todos los libro\n"
        "[bold yellow]3.[/bold yellow]🔄📘  Actualizar datos de un libro\n"
        "[bold yellow]4.[/bold yellow]🗑️📚  Eliminar un libro\n"
        "[bold red]5.[/bold red]🚪  Volver al menú principal"
    )
    console.print(
        Panel(
            menu_p,
            title="[bold]📚  MENÚ DE LIBROS[/bold]",
            subtitle="Seleccione una opción",
            border_style="green",
        )
    )


def menu_prestamos():
    menu_pre=(
        "[bold yellow]1.[/bold yellow]➕  Registrar un nuevo préstamo\n"
        "[bold yellow]2.[/bold yellow]📦  Resgistrar devolución\n"
        "[bold yellow]3.[/bold yellow]📋  Listar los prestamos\n"
        "[bold yellow]4.[/bold yellow]🔙  Listar devoluciones\n"
        "[bold red]5.[/bold red]🚪  Volver al menú principal\n"
    )
    console.print(
        Panel(
            menu_pre,
            title="[bold]🖱️✍️  MENÚ DE PRÉSTAMOS[/bold]",
            subtitle="Seleccione una opción",
            border_style="green",
        )
    )


def main():
    """Función principal que ejecuta el bucle del menú."""


    titulo = Text(" 📚  SISTEMA DE GESTIÓN DE PRÉSTAMOS DE BIBLIOTECA  🏫", justify="center")
    titulo.stylize("bold white on black")

    panel_titulo = Panel(
        titulo,
        title="[bold yellow]Bienvenidos[/bold yellow]",
        subtitle="[bold cyan]Biblioteca Central[/bold cyan]",
        border_style="bright_magenta",
        box=box.DOUBLE,
    )

    console.print(panel_titulo)


    while True:
        console.rule("[bold bright_magenta]🏠 MENÚ PRINCIPAL[/bold bright_magenta]")
        console.print("[yellow]1.[/yellow]👤  Gestionar Clientes")
        console.print("[yellow]2.[/yellow]📚  Gestionar Libros")
        console.print("[yellow]3.[/yellow]📝  Gestionar Préstamos")
        console.print("[yellow]4.[/yellow]🚪  Salir")

        opcion_principal = Prompt.ask("Selecciona una opción", choices=["1", "2", "3","4"], show_choices=False)

        if opcion_principal == '1':

            archivo_seleccionado = elegir_almacenamiento()
            console.print(f"\n👍 Usando el archivo: [bold green]{archivo_seleccionado}[/bold green]")
            # MENÚ DE USUARIOS
            while True:
                menu_usuarios()
                opcion = Prompt.ask("Opción", choices=["1", "2", "3", "4", "5"], show_choices=False)

                if opcion == '1':
                    menu_crear_usuario(archivo_seleccionado)
                elif opcion == '2':
                    menu_leer_usuario(archivo_seleccionado)
                elif opcion == '3':
                    menu_actualizar_usuario(archivo_seleccionado)
                elif opcion == '4':
                    menu_eliminar_usuario(archivo_seleccionado)
                elif opcion == '5':
                    console.print("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
                    break

        elif opcion_principal == '2':

            archivo_seleccionado = elegir_almacenamiento2()
            console.print(f"\n👍 Usando el archivo: [bold green]{archivo_seleccionado}[/bold green]")

            # MENÚ DE LIBROS
            while True:
                menu_libros()
                opcion = Prompt.ask("Opción", choices=["1", "2", "3", "4", "5"], show_choices=False)

                if opcion == '1':
                    menu_crear_libro(archivo_seleccionado)
                elif opcion == "2":
                    menu_leer_libros(archivo_seleccionado)
                elif opcion == "3":
                    menu_actualizar_libro(archivo_seleccionado)
                elif opcion == '4':
                    menu_eliminar_libro(archivo_seleccionado)
                elif opcion == '5':
                    console.print("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
                    break

        elif opcion_principal == '3':
            archivo_libros = ARCHIVO_LIBROS_JSON

            archivo_seleccionado = elegir_almacenamiento3()
            console.print(f"\n👍 Usando el archivo: [bold green]{archivo_seleccionado}[/bold green]")

            #MENU PRÉSTAMOS
            while True:
                menu_prestamos()
                opcion = Prompt.ask(
                    "Opción", choices=["1", "2", "3", "4", "5"], show_choices=False
                )

                if opcion == "1":
                    menu_crear_prestamo(archivo_seleccionado)
                elif opcion == "2":
                    menu_registrar_devolucion(archivo_seleccionado, archivo_libros)
                elif opcion == "3":
                    menu_listar_prestamo(archivo_seleccionado)
                elif opcion == '4':
                   menu_listar_devoluciones_prestamos()
                elif opcion == '5':
                    console.print("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
                    break
        elif opcion_principal == '4':
            console.print(
                Panel.fit(
                    "[bold white]Gracias por usar el sistema de biblioteca 💖[/bold white]\n"
                    "[green]¡Hasta pronto, lector digital! 📖[/green]",
                    border_style="bright_magenta",
                    box=box.DOUBLE_EDGE,
                )
            )
            break

# --- Punto de Entrada del Script ---
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Programa interrumpido por el usuario. Adiós.[/bold red]")