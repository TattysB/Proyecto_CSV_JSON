
from typing import Callable, Optional
from rich.console import Console
from rich.panel import Panel
import sys, os
sys.path.append(os.path.dirname(__file__))

console = Console()

menu_producto: Optional[Callable[[], None]] = None
menu_usuarios: Optional[Callable[[], None]] = None
menu_prestamos: Optional[Callable[[], None]] = None

try:
    from producto import menu_producto as _mproducto
    menu_producto = _mproducto
except Exception as e:
    console.print(f"No se pudo cargar 'producto' ({e}). La opción de productos estará deshabilitada.")

try:

    from gestor_datos import menu_usuarios as _musuarios
    menu_usuarios = _musuarios
except Exception as e:
    console.print(f" No se pudo cargar 'gestor_datos' ({e}). La opción de usuarios estará deshabilitada.")

try:
    from prestamos import menu_prestamos as _mprestamos
    menu_prestamos = _mprestamos
except Exception as e:
    console.print(f"No se pudo cargar 'prestamos' ({e}). La opción de préstamos estará deshabilitada.")


def mostrar_banner() -> None:
    """Muestra el banner de bienvenida."""
    texto = (
        " SISTEMA DE GESTIÓN DE PRÉSTAMOS - BIBLIOTECA  ️\n"
        "-----------------------------------------------\n"
        "Proyecto final - Módulo 3 (ADSO)  |  Grupo 2\n    "
    )
    console.print(Panel.fit(texto, title="[bold cyan]Bienvenido[/bold cyan]", border_style="blue"))


def opcion_habilitada(func: Optional[Callable[[], None]]) -> bool:
    """
    Devuelve True si la opción está disponible (el módulo se importó correctamente).
    """
    return func is not None


def menu_principal() -> None:
    """Bucle principal que muestra el menú y redirige a los submenús."""
    mostrar_banner()
    while True:
        console.print("\n=== MENÚ PRINCIPAL ===")
        console.print("1. Gestión de Productos")
        console.print("2. Gestión de Usuarios")
        console.print("3. Gestión de Préstamos")
        console.print("0. Salir\n")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            if opcion_habilitada(menu_producto):
                try:
                    menu_producto()  # type: ignore
                except Exception as e:
                    console.print(f" Error en módulo productos: {e}")
            else:
                console.print("Módulo de productos no disponible.")

        elif opcion == "2":
            if opcion_habilitada(menu_usuarios):
                try:
                    menu_usuarios()  # type: ignore
                except Exception as e:
                    console.print(f" Error en módulo usuarios: {e}")
            else:
                console.print(" Módulo de usuarios no disponible.")

        elif opcion == "3":
            if opcion_habilitada(menu_prestamos):
                try:
                    menu_prestamos()  # type: ignore
                except Exception as e:
                    console.print(f"Error en módulo préstamos: {e}")
            else:
                console.print("Módulo de préstamos no disponible.")

        elif opcion == "0":
            console.print("\nGracias por usar el sistema. Saludos.")
            break

        else:
            console.print("Opción inválida. Intenta de nuevo.")


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        console.print("\nPrograma interrumpido por el usuario (Ctrl+C).")