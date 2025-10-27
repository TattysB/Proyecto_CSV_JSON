# -*- coding: utf-8 -*-
"""
Módulo Principal - Interfaz de Usuario (UI).

Punto de entrada de la aplicación.
Maneja la interacción con el usuario (menús, entradas, salidas) usando la librería rich.
"""

import os

import usuario
import libro
# import prestamos

# --- Importaciones de la librería Rich ---
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

# --- Inicialización de la Consola de Rich ---
console = Console()

# --- Constantes de Configuración de Rutas ---
DIRECTORIO_DATOS = 'data'
NOMBRE_ARCHIVO_CSV = 'usuario.csv'
NOMBRE_ARCHIVO_JSON = 'usuario.json'
NOMBRE_ARCHIVO_CSV2 = 'libro.csv'
NOMBRE_ARCHIVO_JSON2 = 'libro.json'



# --- CLIENTES ---
def menu_crear_cliente(filepath: str):
    """Maneja la lógica para registrar un nuevo aprendiz."""
    console.print(Panel.fit("[bold cyan]📝 Registrar Nuevo Usuario[/bold cyan]"))

    documento = IntPrompt.ask("Número de Documento")
    nombres = Prompt.ask("Nombres")
    apellidos = Prompt.ask("Apellidos")
    email = Prompt.ask("Email")

    cliente_creado = usuario.crear_usuario(
        filepath, documento, nombres, apellidos, email
    )

    if cliente_creado:
        console.print(Panel(f"✅ ¡Usuario registrado con éxito!\n   ID Asignado: [bold yellow]{cliente_creado['id']}[/bold yellow]",
                            border_style="green", title="Éxito"))
    else:
        console.print(Panel("⚠️ No se pudo registrar al Usuario. Verifique los datos.",
                            border_style="red", title="Error"))

def menu_leer_clientes(filepath: str):
    """Maneja la lógica para mostrar todos los clientes en una tabla."""
    console.print(Panel.fit("[bold cyan]👥 Lista de usuarios[/bold cyan]"))
    clientes = usuario.leer_todos_los_usuario(filepath)

    if not clientes:
        console.print("[yellow]No hay usuarios registrados.[/yellow]")
        return

    # Creamos la tabla
    tabla = Table(title="Usuarios Registrados", border_style="blue", show_header=True, header_style="bold magenta")
    tabla.add_column("ID", style="dim", width=5)
    tabla.add_column("Documento", justify="right")
    tabla.add_column("Nombre Completo")
    tabla.add_column("email", justify="right")

    # Ordenamos por Ficha y luego por ID
    clientes_ordenados = sorted(clientes, key=lambda x: (int(x['documento']), int(x['id'])))

    for ap in clientes_ordenados:

        tabla.add_row(
            ap['id'],
            ap['documento'],
            f"{ap['nombres']} {ap['apellidos']}",
            ap['email']
        )

    console.print(tabla)

def menu_actualizar_cliente(filepath: str):
    """Maneja la lógica para actualizar un aprendiz."""
    console.print(Panel.fit("[bold cyan]✏️ Actualizar Datos del Usuario[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el Documento del usuario a actualizar")

    cliente_actual = usuario.buscar_usuario_por_documento(filepath, str(documento))
    if not cliente_actual:
        console.print("\n[bold red]❌ No se encontró ningún usuario con ese documento.[/bold red]")
        return

    console.print("\nDatos actuales. Presione Enter para no modificar un campo.")
    datos_nuevos = {}

    nombres = Prompt.ask(f"Nombres ({cliente_actual['nombres']})", default=cliente_actual['nombres'])
    if nombres != cliente_actual['nombres']: datos_nuevos['nombres'] = nombres

    apellidos = Prompt.ask(f"Apellidos ({cliente_actual['apellidos']})", default=cliente_actual['apellidos'])
    if apellidos != cliente_actual['apellidos']: datos_nuevos['apellidos'] = apellidos

    email = Prompt.ask(f"Email ({cliente_actual['email']})", default=(cliente_actual['email']))
    if email != (cliente_actual['email']): datos_nuevos['email'] = email

    if not datos_nuevos:
        console.print("\n[yellow]No se modificó ningún dato.[/yellow]")
        return

    cliente_actualizado = usuario.actualizar_usuario(filepath, str(documento), datos_nuevos)
    if cliente_actualizado:
        console.print(Panel("✅ ¡Datos del usuario actualizados con éxito!", border_style="green", title="Éxito"))
    else:
        console.print(Panel("❌ Ocurrió un error al actualizar.", border_style="red", title="Error"))

def menu_eliminar_cliente(filepath: str):
    """Maneja la lógica para eliminar un clientes."""
    console.print(Panel.fit("[bold cyan]🗑️ Eliminar usuario[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el Documento del usuario a eliminar")

    clientes = usuario.buscar_usuario_por_documento(filepath, str(documento))
    if not clientes:
        console.print("\n[bold red]❌ No se encontró ningún usuario con ese documento.[/bold red]")
        return

    confirmacion = Confirm.ask(
        f"¿Está seguro de que desea eliminar a [bold]{clientes['nombres']} {clientes['apellidos']}[/bold]?",
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
        return os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_CSV)
    else:
        return os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_JSON)

# --- PRODUCTO ---

def menu_crear_producto(filepath: str):
    """Maneja la lógica para registrar un nuevo aprendiz."""
    console.print(Panel.fit("[bold cyan]📝 Registrar Nuevo Libro[/bold cyan]"))

    id_producto = IntPrompt.ask("ISBN")
    nombre = Prompt.ask("Nombre")
    autor = Prompt.ask("Autor")
    stock = IntPrompt.ask("Stock")

    producto_creado = libro.crear_libro(
        filepath, id_producto, nombre, autor, stock
    )

    if producto_creado:
        console.print(Panel(
            f"✅ ¡Libro registrado con éxito!\n   ID Asignado: [bold yellow]{producto_creado['id']}[/bold yellow]",
            border_style="green", title="Éxito"))
    else:
        console.print(Panel("⚠️ No se pudo registrar el libro. Verifique los datos.",
                            border_style="red", title="Error"))

def menu_leer_productos(filepath: str):
    """Maneja la lógica para mostrar todos los productos en una tabla."""
    console.print(Panel.fit("[bold cyan]📦 Lista de libro[/bold cyan]"))
    productos = libro.leer_todos_los_libros(filepath)

    if not productos:
        console.print("[yellow]No hay productos registrados.[/yellow]")
        return

    # Creamos la tabla
    tabla = Table(title="Libro Registrados", border_style="blue", show_header=True, header_style="bold magenta")
    tabla.add_column("ID", style="dim", width=5)
    tabla.add_column("ISBN", justify="right")
    tabla.add_column("Nombre")
    tabla.add_column("Autor", justify="right")
    tabla.add_column("Stock", justify="right")

    # Ordenamos por ISDN y luego por ID
    productos_ordenados = sorted(productos, key=lambda x: (int(x.get('ISDN', 0)), int(x.get('id', 0))))

    for ap in productos_ordenados:
        tabla.add_row(
            str(ap.get('id', 'N/A')),
            str(ap.get('ISBN', 'N/A')),
            str(ap.get('nombre', 'N/A')),
            str(ap.get('autor', 'N/A')),
            str(ap.get('stock', 0))
        )

    console.print(tabla)
def menu_actualizar_producto(filepath: str):
    """Maneja la lógica para actualizar un aprendiz."""
    console.print(Panel.fit("[bold cyan]✏️ Actualizar Datos del Libro[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el ISBN del producto a actualizar")

    producto_actual = libro.buscar_libro_por_isbn(filepath, str(documento))
    if not producto_actual:
        console.print("\n[bold red]❌ No se encontró ningún producto con ese ISBN.[/bold red]")
        return

    console.print("\nDatos actuales. Presione Enter para no modificar un campo.")
    datos_nuevos = {}

    nombre = Prompt.ask(f"Nombre ({producto_actual['nombre']})", default=producto_actual['nombre'])
    if nombre != producto_actual['nombre']: datos_nuevos['nombre'] = nombre

    autor = Prompt.ask(f"Autor ({producto_actual['autor']})", default=producto_actual['autor'])
    if autor != producto_actual['autor']: datos_nuevos['autor'] = autor

    stock = IntPrompt.ask(f"Stock ({producto_actual['stock']})", default=(producto_actual['stock']))
    if stock != (producto_actual['stock']): datos_nuevos['stock'] = stock

    if not datos_nuevos:
        console.print("\n[yellow]No se modificó ningún dato.[/yellow]")
        return

    producto_actualizado = libro.actualizar_libro(filepath, str(documento), datos_nuevos)
    if producto_actualizado:
        console.print(Panel("✅ ¡Datos del libro actualizados con éxito!", border_style="green", title="Éxito"))
    else:
        console.print(Panel("❌ Ocurrió un error al actualizar.", border_style="red", title="Error"))

def menu_eliminar_producto(filepath: str):
    """Maneja la lógica para eliminar un clientes."""
    console.print(Panel.fit("[bold cyan]🗑️ Eliminar libro[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el ISBN del libro a eliminar")

    productos = libro.buscar_libro_por_isbn(filepath, str(documento))
    if not productos:
        console.print("\n[bold red]❌ No se encontró ningún producto con ese ISBN.[/bold red]")
        return

    confirmacion = Confirm.ask(
        f"¿Está seguro de que desea eliminar a [bold]{productos['nombre']} [/bold]?",
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
        return os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_CSV2)
    else:
        return os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_JSON2)

# --- LISTAS DE OPCIONES ---

def menu_clientes():
    """Imprime el menú principal en la consola usando un Panel de Rich."""
    menu_c = (
        "[bold yellow]1[/bold yellow]. Registrar un nuevo Usuario\n"
        "[bold yellow]2[/bold yellow]. Ver todos los Usuario\n"
        "[bold yellow]3[/bold yellow]. Actualizar datos de un Usuario\n"
        "[bold yellow]4[/bold yellow]. Eliminar un Usuario\n"
        "[bold red]5[/bold red]. Salir"
    )
    console.print(Panel(menu_c, title="[bold]CLIENTES[/bold]", subtitle="Seleccione una opción", border_style="green"))

def menu_productos():

    menu_p = (
        "[bold yellow]1[/bold yellow]. Registrar un nuevo Libro\n"
        "[bold yellow]2[/bold yellow]. Ver todos los Libro\n"
        "[bold yellow]3[/bold yellow]. Actualizar datos de un Libro\n"
        "[bold yellow]4[/bold yellow]. Eliminar un Libro\n"
        "[bold red]5[/bold red]. Salir"
    )
    console.print(
        Panel(menu_p, title="[bold]CLIENTES[/bold]", subtitle="Seleccione una opción", border_style="green"))

def main():
    """Función principal que ejecuta el bucle del menú."""


    while True:
        console.print("[yellow]1.[/yellow] Gestionar Usuarios")
        console.print("[yellow]2.[/yellow] Gestionar Libros")
        console.print("[yellow]3.[/yellow] Salir")

        opcion_principal = Prompt.ask("Selecciona una opción", choices=["1", "2", "3"], show_choices=False)

        if opcion_principal == '1':

            archivo_seleccionado = elegir_almacenamiento()
            console.print(f"\n👍 Usando el archivo: [bold green]{archivo_seleccionado}[/bold green]")
            # MENÚ DE CLIENTES
            while True:
                menu_clientes()
                opcion = Prompt.ask("Opción", choices=["1", "2", "3", "4", "5"], show_choices=False)

                if opcion == '1':
                    menu_crear_cliente(archivo_seleccionado)
                elif opcion == '2':
                    menu_leer_clientes(archivo_seleccionado)
                elif opcion == '3':
                    menu_actualizar_cliente(archivo_seleccionado)
                elif opcion == '4':
                    menu_eliminar_cliente(archivo_seleccionado)
                elif opcion == '5':
                    console.print("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
                    break

        elif opcion_principal == '2':

            archivo_seleccionado = elegir_almacenamiento2()
            console.print(f"\n👍 Usando el archivo: [bold green]{archivo_seleccionado}[/bold green]")
            # MENÚ DE PRODUCTOS
            while True:
                menu_productos()
                opcion = Prompt.ask("Opción", choices=["1", "2", "3", "4", "5"], show_choices=False)

                if opcion == '1':
                    menu_crear_producto(archivo_seleccionado)
                elif opcion == '2':
                    menu_leer_productos(archivo_seleccionado)
                elif opcion == '3':
                    menu_actualizar_producto(archivo_seleccionado)
                elif opcion == '4':
                    menu_eliminar_producto(archivo_seleccionado)
                elif opcion == '5':
                    console.print("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
                    break

        elif opcion_principal == '3':
            console.print("\n[bold magenta]👋 ¡Hasta luego! Gracias por usar la agenda.[/bold magenta]")
            break

# --- Punto de Entrada del Script ---
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Programa interrumpido por el usuario. Adiós.[/bold red]")

