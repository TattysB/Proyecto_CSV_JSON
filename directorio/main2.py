# -*- coding: utf-8 -*-
"""
Módulo Principal - Interfaz de Usuario (UI).

Punto de entrada de la aplicación.
Maneja la interacción con el usuario (menús, entradas, salidas) usando la librería rich.
"""
import email
import os

import usuario  # Importamos nuestro módulo de lógica de negocio
import libro
import prestamos

# --- Importaciones de la librería Rich ---
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt, FloatPrompt
from rich.table import Table

# from Proyecto_CSV_JSON.directorio.prestamos import realizar_prestamo

# --- Inicialización de la Consola de Rich ---
console = Console()

# --- Constantes de Configuración de Rutas ---
DIRECTORIO_DATOS = 'data'
NOMBRE_ARCHIVO_CSV = 'clientes.csv'
NOMBRE_ARCHIVO_JSON = 'clientes.json'
NOMBRE_ARCHIVO_CSV2 = 'productos.csv'
NOMBRE_ARCHIVO_JSON2 = 'productos.json'
NOMBRE_ARCHIVO_CSV3 = 'préstamos.csv'
NOMBRE_ARCHIVO_JSON3 = 'préstamos.json'



# --- CLIENTES ---
def menu_crear_cliente(filepath: str):
    """Maneja la lógica para registrar un nuevo aprendiz."""
    console.print(Panel.fit("[bold cyan]📝 Registrar Nuevo Cliente[/bold cyan]"))

    documento = IntPrompt.ask("Número de Documento")
    nombres = Prompt.ask("Nombres")
    apellidos = Prompt.ask("Apellidos")
    email = Prompt.ask("Email")

    cliente_creado = cliente.crear_cliente(
        filepath, documento, nombres, apellidos, email
    )

    if cliente_creado:
        console.print(Panel(f"✅ ¡Cliente registrado con éxito!\n   ID Asignado: [bold yellow]{cliente_creado['id']}[/bold yellow]",
                            border_style="green", title="Éxito"))
    else:
        console.print(Panel("⚠️ No se pudo registrar al cliente. Verifique los datos.",
                            border_style="red", title="Error"))

def menu_leer_clientes(filepath: str):
    """Maneja la lógica para mostrar todos los clientes en una tabla."""
    console.print(Panel.fit("[bold cyan]👥 Lista de clientes[/bold cyan]"))
    clientes = cliente.leer_todos_los_clientes(filepath)

    if not clientes:
        console.print("[yellow]No hay clientes registrados.[/yellow]")
        return

    # Creamos la tabla
    tabla = Table(title="Clientes Registrados", border_style="blue", show_header=True, header_style="bold magenta")
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
    console.print(Panel.fit("[bold cyan]✏️ Actualizar Datos del Cliente[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el Documento del cliente a actualizar")

    cliente_actual = cliente.buscar_cliente_por_documento(filepath, str(documento))
    if not cliente_actual:
        console.print("\n[bold red]❌ No se encontró ningún cliente con ese documento.[/bold red]")
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

    cliente_actualizado = cliente.actualizar_cliente(filepath, str(documento), datos_nuevos)
    if cliente_actualizado:
        console.print(Panel("✅ ¡Datos del cliente actualizados con éxito!", border_style="green", title="Éxito"))
    else:
        console.print(Panel("❌ Ocurrió un error al actualizar.", border_style="red", title="Error"))

def menu_eliminar_cliente(filepath: str):
    """Maneja la lógica para eliminar un clientes."""
    console.print(Panel.fit("[bold cyan]🗑️ Eliminar Aprendiz[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el Documento del clientes a eliminar")

    clientes = cliente.buscar_cliente_por_documento(filepath, str(documento))
    if not clientes:
        console.print("\n[bold red]❌ No se encontró ningún clientes con ese documento.[/bold red]")
        return

    confirmacion = Confirm.ask(
        f"¿Está seguro de que desea eliminar a [bold]{clientes['nombres']} {clientes['apellidos']}[/bold]?",
        default=False
    )

    if confirmacion:
        if cliente.eliminar_cliente(filepath, str(documento)):
            console.print(Panel("✅ ¡Cliente eliminado con éxito!", border_style="green", title="Éxito"))
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
    console.print(Panel.fit("[bold cyan]📝 Registrar Nuevo Producto[/bold cyan]"))

    id_producto = IntPrompt.ask("ISDN")
    nombre = Prompt.ask("Nombre")
    precio = FloatPrompt.ask("Precio")
    stock = IntPrompt.ask("Stock")

    producto_creado = libro.crear_producto(
        filepath, id_producto, nombre, precio, stock
    )

    if producto_creado:
        console.print(Panel(
            f"✅ ¡Producto registrado con éxito!\n   ID Asignado: [bold yellow]{producto_creado['id']}[/bold yellow]",
            border_style="green", title="Éxito"))
    else:
        console.print(Panel("⚠️ No se pudo registrar el prodcuto. Verifique los datos.",
                            border_style="red", title="Error"))

def menu_leer_productos(filepath: str):
    """Maneja la lógica para mostrar todos los productos en una tabla."""
    console.print(Panel.fit("[bold cyan]👥 Lista de productos[/bold cyan]"))
    productos = libro.leer_todos_los_productos(filepath)

    if not productos:
        console.print("[yellow]No hay productos registrados.[/yellow]")
        return

    # Creamos la tabla
    tabla = Table(title="Clientes Registrados", border_style="blue", show_header=True, header_style="bold magenta")
    tabla.add_column("ID", style="dim", width=5)
    tabla.add_column("ISDN", justify="right")
    tabla.add_column("nombre")
    tabla.add_column("precio")
    tabla.add_column("stock", justify="right")

    # Ordenamos por Ficha y luego por ID
    productos_ordenados = sorted(productos, key=lambda x: (int(x['ISDN']), int(x['id'])))

    for ap in productos_ordenados:

        tabla.add_row(
            ap['id'],
            ap['ISDN'],
            ap['nombre'],
            ap['precio'],
            ap['stock'],
        )

    console.print(tabla)

def menu_actualizar_producto(filepath: str):
    """Maneja la lógica para actualizar un aprendiz."""
    console.print(Panel.fit("[bold cyan]✏️ Actualizar Datos del Producto[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el ISDN del producto a actualizar")

    producto_actual = libro.buscar_producto_por_isdn(filepath, str(documento))
    if not producto_actual:
        console.print("\n[bold red]❌ No se encontró ningún producto con ese ISDN.[/bold red]")
        return

    console.print("\nDatos actuales. Presione Enter para no modificar un campo.")
    datos_nuevos = {}

    nombre = Prompt.ask(f"Nombre ({producto_actual['nombre']})", default=producto_actual['nombre'])
    if nombre != producto_actual['nombre']: datos_nuevos['nombre'] = nombre

    precio = FloatPrompt.ask(f"Precio ({producto_actual['precio']})", default=producto_actual['precio'])
    if precio != producto_actual['precio']: datos_nuevos['precio'] = precio

    stock = IntPrompt.ask(f"Stock ({producto_actual['stock']})", default=(producto_actual['stock']))
    if stock != (producto_actual['stock']): datos_nuevos['stock'] = stock

    if not datos_nuevos:
        console.print("\n[yellow]No se modificó ningún dato.[/yellow]")
        return

    producto_actualizado = libro.actualizar_producto(filepath, str(documento), datos_nuevos)
    if producto_actualizado:
        console.print(Panel("✅ ¡Datos del cliente actualizados con éxito!", border_style="green", title="Éxito"))
    else:
        console.print(Panel("❌ Ocurrió un error al actualizar.", border_style="red", title="Error"))

def menu_eliminar_producto(filepath: str):
    """Maneja la lógica para eliminar un clientes."""
    console.print(Panel.fit("[bold cyan]🗑️ Eliminar Aprendiz[/bold cyan]"))
    documento = IntPrompt.ask("Ingrese el Documento del clientes a eliminar")

    productos = libro.buscar_producto_por_isdn(filepath, str(documento))
    if not productos:
        console.print("\n[bold red]❌ No se encontró ningún producto con ese ISDN.[/bold red]")
        return

    confirmacion = Confirm.ask(
        f"¿Está seguro de que desea eliminar a [bold]{productos['nombre']} [/bold]?",
        default=False
    )

    if confirmacion:
        if libro.eliminar_producto(filepath, str(documento)):
            console.print(Panel("✅ ¡Producto eliminado con éxito!", border_style="green", title="Éxito"))
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

#----PRÉSTAMO----

def menu_crear_prestamo(filepath: str):
    """Maneja la lógica para registrar un nuevo préstamo"""
    console.print(Panel.fit("[bold cyan]📝 Registrar nuevo préstamo[/bold cyan]"))

    id_cliente = Prompt.ask("ID del cliente")
    id_producto = Prompt.ask("ID del producto")

    prestamo_creado = prestamos.realizar_prestamo(
        os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_JSON3),  # préstamos
        os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_JSON),   # clientes
        os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_JSON2),  # productos
        id_cliente,
        id_producto
    )



    if prestamo_creado:
        console.print(Panel.fit(
            f"✅ ¡Préstamo registrado con éxito!\nID Asignado: [bold yellow]{prestamo_creado['id_prestamo']}[/bold yellow]",
            border_style="green", title="Éxito"
        ))
    else:
        console.print(Panel.fit(
            "⚠️  No se pudo registrar el préstamo. Verifique los datos.",
            border_style="red", title="Error"
        ))


def menu_registrar_devolucion(filepath:str):
    """Maneja la lógica para registrar la devolucion """
    console.print(Panel.fit("[bold cyan]📦 Registrar devolución[/bold cyan]"))

    id_prestamo=Prompt.ask("id_prestamo")

    devolucion_creado=prestamos.registrar_devolucion(filepath,id_prestamo)

    if devolucion_creado:
        console.print(Panel.fit(
             f"\n✅ ¡Devolución registrada correctamente!\n ID Asignado: [bold yellow] {devolucion_creado['id']}[/bold yellow] ",
             border_style="green",title="Éxito" ))
    else:
        console.print(Panel.fit(
            f"\n❌  No se encontró el préstamo o ya fue devuelto",
            border_style="red",title="Error" ))


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
        return os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_CSV3)
    else:
        return os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_JSON3)


# --- LISTAS DE OPCIONES ---

def menu_clientes():
    """Imprime el menú principal en la consola usando un Panel de Rich."""
    menu_c = (
        "[bold yellow]1[/bold yellow]. Registrar un nuevo cliente\n"
        "[bold yellow]2[/bold yellow]. Ver todos los clientes\n"
        "[bold yellow]3[/bold yellow]. Actualizar datos de un cliente\n"
        "[bold yellow]4[/bold yellow]. Eliminar un cliente\n"
        "[bold red]5[/bold red]. Salir"
    )
    console.print(Panel(menu_c, title="[bold]CLIENTES[/bold]", subtitle="Seleccione una opción", border_style="green"))

def menu_productos():

    menu_p = (
        "[bold yellow]1[/bold yellow]. Registrar un nuevo producto\n"
        "[bold yellow]2[/bold yellow]. Ver todos los producto\n"
        "[bold yellow]3[/bold yellow]. Actualizar datos de un producto\n"
        "[bold yellow]4[/bold yellow]. Eliminar un producto\n"
        "[bold red]5[/bold red]. Salir"
    )
    console.print(
        Panel(menu_p, title="[bold]CLIENTES[/bold]", subtitle="Seleccione una opción", border_style="green"))

def menu_prestamos():
    menu_pre=(
        "[bold yellow]1[/bold yellow]. Registrar un nuevo préstamo\n"
        "[bold yellow]2[/bold yellow]. Resgistrar devolución\n"
        "[bold red]3[/bold red]. Salir"
    )
    console.print(
        Panel(menu_pre, title="[bold]PRÉSTAMOS[/bold]", subtitle="Seleccione una opción", border_style="green"))

def main():
    """Función principal que ejecuta el bucle del menú."""


    while True:
        console.print("[yellow]1.[/yellow] Gestionar Clientes")
        console.print("[yellow]2.[/yellow] Gestionar Productos")
        console.print("[yellow]3.[/yellow] Gestionar Préstamos")
        console.print("[yellow]4.[/yellow] Salir")

        opcion_principal = Prompt.ask("Selecciona una opción", choices=["1", "2", "3","4"], show_choices=False)

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
            archivo_seleccionado = elegir_almacenamiento3()
            console.print(f"\n👍 Usando el archivo: [bold green]{archivo_seleccionado}[/bold green]")
            #MENU PRÉSTAMOS
            while True:
                menu_prestamos()
                opcion=Prompt.ask("Opción",choices=["1","2","3"],show_choices=False)

                if opcion == '1':
                    menu_crear_prestamo(archivo_seleccionado)
                elif opcion == '2':
                    menu_registrar_devolucion(archivo_seleccionado)
                elif opcion == '3':
                    console.print("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
                    break
        elif opcion_principal == '4':
            console.print("\n[bold magenta]👋 ¡Hasta luego! Gracias por usar la agenda.[/bold magenta]")
            break

# --- Punto de Entrada del Script ---
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Programa interrumpido por el usuario. Adiós.[/bold red]")