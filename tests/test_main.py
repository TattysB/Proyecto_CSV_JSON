import os
import sys
from unittest import mock
from rich.panel import Panel
from rich.table import Table
from rich.text import Text # Importar Text para algunos asserts si es necesario
from rich import box # Importar box si es necesario para los asserts de Panel


# Asegurarse de que el directorio raíz del proyecto esté en sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar 'main' como un módulo estándar.
import main

# Importar Rich aquí para poder parchear sus componentes directamente
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm # Importar explícitamente para el mocking
from rich.table import Table # Importar explícitamente para los asserts

# --- Corrección en main.py (debe aplicarse también en tu archivo main.py) ---
# Es crucial que las funciones elegir_almacenamiento y elegir_almacenamiento2
# devuelvan las rutas correctas según la elección.
# ORIGINALMENTE ESTABAN INVERTIDAS. ESTO YA ESTÁ REFLEJADO EN EL TEST CORREGIDO.

# PARA TU main.py, ASEGÚRATE DE QUE SE VEAN ASÍ:
# def elegir_almacenamiento() -> str:
#     # ... (código existente) ...
#     if opcion == '1': # Elige CSV
#         return os.path.join(DIRECTORIO_DATOS, ARCHIVO_USUARIOS_CSV) # Retorna CSV
#     else: # Elige JSON (por defecto o '2')
#         return os.path.join(DIRECTORIO_DATOS, ARCHIVO_USUARIOS_JSON) # Retorna JSON

# def elegir_almacenamiento2() -> str:
#     # ... (código existente) ...
#     if opcion == '1': # Elige CSV
#         return os.path.join(DIRECTORIO_DATOS, ARCHIVO_LIBROS_CSV) # Retorna CSV
#     else: # Elige JSON (por defecto o '2')
#         return os.path.join(DIRECTORIO_DATOS, ARCHIVO_LIBROS_JSON) # Retorna JSON
# --------------------------------------------------------------------------------


class BaseTestWithMocks:
    """Clase base para pruebas que necesitan mocks comunes."""

    def setup_method(self):
        """Prepara los mocks antes de cada prueba."""
        # Se parchean los componentes de Rich directamente desde sus módulos originales
        # y los módulos de lógica de negocio (usuario, libro, prestamos) del módulo 'main'.
        self.patcher_rich_components = mock.patch.multiple(
            'rich.prompt',
            Prompt=mock.DEFAULT,
            IntPrompt=mock.DEFAULT,
            Confirm=mock.DEFAULT,
        )
        self.patcher_main_modules = mock.patch.multiple(
            main, # Módulo main donde están usuario, libro, prestamos importados
            usuario=mock.DEFAULT,
            libro=mock.DEFAULT,
            prestamos=mock.DEFAULT, # Añadido el mock para el módulo prestamos
            # También mockeamos las constantes de los archivos para asegurar que _mock_os_path_join_side_effect funcione
            ARCHIVO_USUARIOS_CSV=mock.DEFAULT,
            ARCHIVO_USUARIOS_JSON=mock.DEFAULT,
            ARCHIVO_LIBROS_CSV=mock.DEFAULT,
            ARCHIVO_LIBROS_JSON=mock.DEFAULT,
            ARCHIVO_PRESTAMOS_CSV=mock.DEFAULT,
            ARCHIVO_PRESTAMOS_JSON=mock.DEFAULT,
            DIRECTORIO_DATOS=mock.DEFAULT, # Mockeamos también DIRECTORIO_DATOS
            BASE_DIR=mock.DEFAULT, # Mockeamos BASE_DIR si es usado en rutas relativas
        )
        self.patcher_console = mock.patch('main.console', spec=Console) # Se parcha la instancia de console en main

        # Se inicializan todos los parcheos
        self.mocks = {}
        self.mocks.update(self.patcher_rich_components.start())
        self.mocks.update(self.patcher_main_modules.start())
        self.mocks['console'] = self.patcher_console.start()

        # Aseguramos que el método .print de la consola mockeada también sea un mock.Mock
        self.mocks['console'].print = mock.Mock()

        # Configurar los mocks para las constantes de main.py
        self.mocks['ARCHIVO_USUARIOS_CSV'] = "usuario.csv"
        self.mocks['ARCHIVO_USUARIOS_JSON'] = "usuario.json"
        self.mocks['ARCHIVO_LIBROS_CSV'] = "libro.csv"
        self.mocks['ARCHIVO_LIBROS_JSON'] = "libro.json"
        self.mocks['ARCHIVO_PRESTAMOS_CSV'] = "prestamo.csv"
        self.mocks['ARCHIVO_PRESTAMOS_JSON'] = "prestamo.json"
        self.mocks['DIRECTORIO_DATOS'] = "/mock/data"
        self.mocks['BASE_DIR'] = "/mock/project_root"


        # Se parcha os.path.join para devolver rutas consistentes en las pruebas
        # También os.makedirs y os.path.exists si main los usa directamente
        self._os_path_join_patcher = mock.patch(
            'os.path.join', side_effect=self._mock_os_path_join_side_effect
        )
        self._os_makedirs_patcher = mock.patch('os.makedirs', return_value=None)
        self._os_path_exists_patcher = mock.patch('os.path.exists', return_value=True) # Asumimos que existen los archivos para tests

        self.mocks['os_path_join'] = self._os_path_join_patcher.start()
        self.mocks['os_makedirs'] = self._os_makedirs_patcher.start()
        self.mocks['os_path_exists'] = self._os_path_exists_patcher.start()


    def teardown_method(self):
        """Limpia los mocks después de cada prueba."""
        self.patcher_rich_components.stop()
        self.patcher_main_modules.stop()
        self.patcher_console.stop()
        self._os_path_join_patcher.stop()
        self._os_makedirs_patcher.stop()
        self._os_path_exists_patcher.stop()
        self.mocks = {}

    def _mock_os_path_join_side_effect(self, dir_path: str, file_name: str) -> str:
        """Side effect para mockear os.path.join consistentemente."""
        # Esta lógica ahora usa las constantes mockeadas de main para mayor coherencia
        if dir_path == self.mocks['DIRECTORIO_DATOS']:
            if file_name == self.mocks['ARCHIVO_USUARIOS_CSV']:
                return f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_USUARIOS_CSV']}"
            elif file_name == self.mocks['ARCHIVO_USUARIOS_JSON']:
                return f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_USUARIOS_JSON']}"
            elif file_name == self.mocks['ARCHIVO_LIBROS_CSV']:
                return f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_LIBROS_CSV']}"
            elif file_name == self.mocks['ARCHIVO_LIBROS_JSON']:
                return f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_LIBROS_JSON']}"
            elif file_name == self.mocks['ARCHIVO_PRESTAMOS_CSV']:
                return f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_PRESTAMOS_CSV']}"
            elif file_name == self.mocks['ARCHIVO_PRESTAMOS_JSON']:
                return f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_PRESTAMOS_JSON']}"
        # Para llamadas a os.path.join que no sean dentro de DIRECTORIO_DATOS (ej. BASE_DIR)
        elif dir_path == self.mocks['BASE_DIR'] and file_name == "data":
            return self.mocks['DIRECTORIO_DATOS']
        elif dir_path == "/mock/project_root" and file_name in ["prestamo.json", "usuario.json", "libro.json"]:
            # Esto es para el caso de menu_crear_prestamo que construye rutas a mano
            return f"/mock/project_root/{file_name}"

        return os.path.join(dir_path, file_name) # Fallback para comportamiento normal si no hay mock específico


class TestUsuarios(BaseTestWithMocks): # Cambiado de TestClientes a TestUsuarios

    def test_menu_crear_usuario_exitoso(self):
        test_filepath = "/mock/data/usuario.json" # Asumiendo JSON para este test

        self.mocks['IntPrompt'].ask.return_value = 123
        self.mocks['Prompt'].ask.side_effect = ["Juan", "Perez", "juan@example.com"]
        self.mocks['usuario'].crear_usuario.return_value = {'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'}

        main.menu_crear_usuario(test_filepath) # Cambiado a menu_crear_usuario

        self.mocks['IntPrompt'].ask.assert_called_once_with("Número de Documento")
        assert self.mocks['Prompt'].ask.call_args_list[0].args[0] == "Nombres"
        assert self.mocks['Prompt'].ask.call_args_list[1].args[0] == "Apellidos"
        assert self.mocks['Prompt'].ask.call_args_list[2].args[0] == "Email"
        self.mocks['usuario'].crear_usuario.assert_called_once_with(test_filepath, 123, "Juan", "Perez", "juan@example.com") # Cambiado a crear_usuario
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="green", title="Éxito"))

    def test_menu_leer_usuario_con_datos(self): # Cambiado a menu_leer_usuario
        test_filepath = "/mock/data/usuario.json"

        self.mocks['usuario'].leer_todos_los_usuario.return_value = [{'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'}] # Cambiado a leer_todos_los_usuario

        main.menu_leer_usuario(test_filepath) # Cambiado a menu_leer_usuario

        self.mocks['usuario'].leer_todos_los_usuario.assert_called_once_with(test_filepath) # Cambiado a leer_todos_los_usuario
        assert any(isinstance(call.args[0], Table) for call in self.mocks['console'].print.call_args_list)

    def test_menu_actualizar_usuario_exitoso(self): # Cambiado a menu_actualizar_usuario
        test_filepath = "/mock/data/usuario.json"

        self.mocks['IntPrompt'].ask.return_value = 123
        self.mocks['usuario'].buscar_usuario_por_documento.return_value = {'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'} # Cambiado a buscar_usuario_por_documento
        self.mocks['Prompt'].ask.side_effect = ["Juan", "Perez", "nuevo.juan@example.com"]
        self.mocks['usuario'].actualizar_usuario.return_value = True # Cambiado a actualizar_usuario

        main.menu_actualizar_usuario(test_filepath) # Cambiado a menu_actualizar_usuario

        self.mocks['usuario'].buscar_usuario_por_documento.assert_called_once_with(test_filepath, "123") # Cambiado a buscar_usuario_por_documento
        self.mocks['usuario'].actualizar_usuario.assert_called_once_with(test_filepath, "123", {'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'nuevo.juan@example.com'}) # Cambiado a actualizar_usuario y ajustado el dict de datos_nuevos
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Datos del usuario actualizados con éxito!", border_style="green", title="Éxito"))

    def test_menu_eliminar_usuario_confirmado(self): # Cambiado a menu_eliminar_usuario
        test_filepath = "/mock/data/usuario.json"

        self.mocks['IntPrompt'].ask.return_value = 123
        self.mocks['usuario'].buscar_usuario_por_documento.return_value = {'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'} # Cambiado a buscar_usuario_por_documento
        self.mocks['Confirm'].ask.return_value = True
        self.mocks['usuario'].eliminar_usuario.return_value = True # Cambiado a eliminar_usuario

        main.menu_eliminar_usuario(test_filepath) # Cambiado a menu_eliminar_usuario

        self.mocks['usuario'].buscar_usuario_por_documento.assert_called_once_with(test_filepath, "123") # Cambiado a buscar_usuario_por_documento
        self.mocks['Confirm'].ask.assert_called_once()
        self.mocks['usuario'].eliminar_usuario.assert_called_once_with(test_filepath, "123") # Cambiado a eliminar_usuario
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Usuario eliminado con éxito!", border_style="green", title="Éxito"))


class TestLibros(BaseTestWithMocks):

    def test_menu_crear_libro_exitoso(self): # Cambiado de producto a libro
        test_filepath = "/mock/data/libro.json"

        self.mocks['IntPrompt'].ask.side_effect = [9781234567890, 5]
        self.mocks['Prompt'].ask.side_effect = ["El Gran Gatsby", "F. Scott Fitzgerald"]
        self.mocks['libro'].crear_libro.return_value = {'id': '1', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5} # Cambiado a crear_libro

        main.menu_crear_libro(test_filepath) # Cambiado a menu_crear_libro

        assert self.mocks['IntPrompt'].ask.call_args_list[0].args[0] == "ISBN"
        assert self.mocks['Prompt'].ask.call_args_list[0].args[0] == "Nombre"
        assert self.mocks['Prompt'].ask.call_args_list[1].args[0] == "Autor"
        assert self.mocks['IntPrompt'].ask.call_args_list[1].args[0] == "Stock"
        self.mocks['libro'].crear_libro.assert_called_once_with(test_filepath, 9781234567890, "El Gran Gatsby", "F. Scott Fitzgerald", 5) # Cambiado a crear_libro
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="green", title="Éxito"))

    def test_menu_leer_libros_con_datos(self): # Cambiado de productos a libros
        test_filepath = "/mock/data/libro.json"

        self.mocks['libro'].leer_todos_los_libros.return_value = [{'id': '1', 'ISBN': '978123', 'nombre': 'Libro Test', 'autor': 'Autor Test', 'stock': 10}] # Cambiado a leer_todos_los_libros

        main.menu_leer_libros(test_filepath) # Cambiado a menu_leer_libros

        self.mocks['libro'].leer_todos_los_libros.assert_called_once_with(test_filepath) # Cambiado a leer_todos_los_libros
        assert any(isinstance(call.args[0], Table) for call in self.mocks['console'].print.call_args_list)

    def test_menu_actualizar_libro_exitoso(self): # Cambiado de producto a libro
        test_filepath = "/mock/data/libro.json"

        self.mocks['IntPrompt'].ask.side_effect = [9781234567890, 10]
        self.mocks['libro'].buscar_libro_por_isbn.return_value = {'id': '1', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5} # Cambiado a buscar_libro_por_isbn
        self.mocks['Prompt'].ask.side_effect = ["El Gran Gatsby", "F. Scott Fitzgerald"] # Nombre y autor no cambian
        self.mocks['libro'].actualizar_libro.return_value = True # Cambiado a actualizar_libro

        main.menu_actualizar_libro(test_filepath) # Cambiado a menu_actualizar_libro

        self.mocks['libro'].buscar_libro_por_isbn.assert_called_once_with(test_filepath, "9781234567890") # Cambiado a buscar_libro_por_isbn
        # Asegúrate de que el diccionario de datos_nuevos coincida con cómo main lo construye
        self.mocks['libro'].actualizar_libro.assert_called_once_with(test_filepath, "9781234567890", {'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 10}) # Cambiado a actualizar_libro
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Datos del libro actualizados con éxito!", border_style="green", title="Éxito"))

    def test_menu_eliminar_libro_confirmado(self): # Cambiado de producto a libro
        test_filepath = "/mock/data/libro.json"

        self.mocks['IntPrompt'].ask.return_value = 9781234567890
        self.mocks['libro'].buscar_libro_por_isbn.return_value = {'id': '1', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5} # Cambiado a buscar_libro_por_isbn
        self.mocks['Confirm'].ask.return_value = True
        self.mocks['libro'].eliminar_libro.return_value = True # Cambiado a eliminar_libro

        main.menu_eliminar_libro(test_filepath) # Cambiado a menu_eliminar_libro

        self.mocks['libro'].buscar_libro_por_isbn.assert_called_once_with(test_filepath, "9781234567890") # Cambiado a buscar_libro_por_isbn
        self.mocks['Confirm'].ask.assert_called_once()
        self.mocks['libro'].eliminar_libro.assert_called_once_with(test_filepath, "9781234567890") # Cambiado a eliminar_libro
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Libro eliminado con éxito!", border_style="green", title="Éxito"))


class TestPrestamos(BaseTestWithMocks): # Nueva clase para tests de Prestamos

    def test_menu_crear_prestamo_exitoso(self):
        test_filepath = "/mock/data/prestamo.json" # La ruta de la llamada inicial no es usada por crear_prestamo
        # main.menu_crear_prestamo usa ARCHIVO_PRESTAMOS_JSON, ARCHIVO_USUARIOS_JSON, ARCHIVO_LIBROS_JSON
        # Mockeamos el os.path.join para estas rutas internas
        self.mocks['os_path_join'].side_effect = self._mock_os_path_join_side_effect

        self.mocks['Prompt'].ask.side_effect = ["user123", "book456"]
        self.mocks['prestamos'].realizar_prestamo.return_value = {'id_prestamo': 'P001', 'id_usuario': 'user123', 'id_libro': 'book456'}

        main.menu_crear_prestamo(test_filepath)

        self.mocks['Prompt'].ask.call_args_list[0].args[0] == "ID del usuario"
        self.mocks['Prompt'].ask.call_args_list[1].args[0] == "ID del libro"
        self.mocks['prestamos'].realizar_prestamo.assert_called_once_with(
            f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_PRESTAMOS_JSON']}", # Estas rutas son generadas internamente
            f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_USUARIOS_JSON']}",
            f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_LIBROS_JSON']}",
            "user123", "book456"
        )
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="green", title="Éxito"))


    def test_menu_registrar_devolucion_exitoso(self):
        test_filepath = "/mock/data/prestamo.json"
        test_libros_filepath = "/mock/data/libro.json"

        self.mocks['Prompt'].ask.return_value = "P001"
        self.mocks['prestamos'].registrar_devolucion.return_value = {'id_prestamo': 'P001', 'estado': 'devuelto'}

        main.menu_registrar_devolucion(test_filepath, test_libros_filepath)

        self.mocks['Prompt'].ask.assert_called_once_with("id_prestamo")
        self.mocks['prestamos'].registrar_devolucion.assert_called_once_with(test_filepath, test_libros_filepath, "P001")
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="green", title="Éxito"))

    def test_menu_listar_prestamo_con_datos(self):
        test_filepath = "/mock/data/prestamo.json"
        # main.menu_listar_prestamo construye rutas para usuario.json y libro.json
        # Aseguramos que el mock de os.path.join maneje estas rutas
        self.mocks['os_path_join'].side_effect = self._mock_os_path_join_side_effect

        self.mocks['prestamos'].listar_prestamos.return_value = [
            {'id_prestamo': 'P001', 'usuario': 'Juan Perez', 'libro': 'El Gran Gatsby',
             'fecha_prestamo': '2023-01-01', 'fecha_devolucion_esperada': '2023-01-15', 'estado': 'prestado'}
        ]

        main.menu_listar_prestamo(test_filepath)

        self.mocks['prestamos'].listar_prestamos.assert_called_once_with(
            # Las rutas que se pasan a listar_prestamos internamente en main.py
            os.path.join("directorio", "data", "prestamo.json"),
            os.path.join("directorio", "data", "usuario.json"),
            os.path.join("directorio", "data", "libro.json")
        )
        assert any(isinstance(call.args[0], Table) for call in self.mocks['console'].print.call_args_list)

    def test_menu_listar_devoluciones_prestamos_con_datos(self):
        # main.menu_listar_devoluciones_prestamos construye rutas para usuario.json y libro.json
        self.mocks['os_path_join'].side_effect = self._mock_os_path_join_side_effect

        self.mocks['prestamos'].listar_devoluciones.return_value = [
            {'id_prestamo': 'P001', 'usuario': 'Juan Perez', 'libro': 'El Gran Gatsby',
             'fecha_prestamo': '2023-01-01', 'fecha_devolucion_esperada': '2023-01-15', 'estado': 'devuelto'}
        ]

        main.menu_listar_devoluciones_prestamos()

        self.mocks['prestamos'].listar_devoluciones.assert_called_once_with(
            # Las rutas que se pasan a listar_devoluciones internamente en main.py
            os.path.join("directorio", "data", "prestamo.json"),
            os.path.join("directorio", "data", "usuario.json"),
            os.path.join("directorio", "data", "libro.json")
        )
        assert any(isinstance(call.args[0], Table) for call in self.mocks['console'].print.call_args_list)


class TestMainLogic(BaseTestWithMocks):

    def test_main_exit_option(self):
        # Para que el bucle se detenga después de la opción de salida
        self.mocks['Prompt'].ask.side_effect = ["4"] # Cambiado a "4" para Salir del menú principal

        main.main()

        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="bright_magenta", box=box.DOUBLE_EDGE)) # Mensaje final de salida

    def test_main_access_client_menu_and_exit(self):
        # 1 (Gestionar Clientes) -> elige almacenamiento -> 5 (Volver) -> 4 (Salir del main)
        self.mocks['Prompt'].ask.side_effect = ["1", "2", "5", "4"] # "2" para elegir JSON, "5" para salir del menú de usuarios, "4" para salir del main

        main.main()

        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="bright_magenta", box=box.DOUBLE_EDGE)) # Mensaje final de salida

    def test_main_access_book_menu_and_exit(self):
        # 2 (Gestionar Libros) -> elige almacenamiento -> 5 (Volver) -> 4 (Salir del main)
        self.mocks['Prompt'].ask.side_effect = ["2", "2", "5", "4"] # "2" para elegir JSON, "5" para salir del menú de libros, "4" para salir del main

        main.main()

        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="bright_magenta", box=box.DOUBLE_EDGE)) # Mensaje final de salida

    def test_main_access_prestamos_menu_and_exit(self):
        # 3 (Gestionar Préstamos) -> elige almacenamiento -> 5 (Volver) -> 4 (Salir del main)
        self.mocks['Prompt'].ask.side_effect = ["3", "2", "5", "4"] # "2" para elegir JSON, "5" para salir del menú de préstamos, "4" para salir del main

        main.main()

        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="bright_magenta", box=box.DOUBLE_EDGE)) # Mensaje final de salida


    def test_elegir_almacenamiento_csv(self):
        self.mocks['Prompt'].ask.return_value = "1" # CSV

        result = main.elegir_almacenamiento()
        self.mocks['console'].print.assert_any_call(Panel.fit(mock.ANY))
        # Asegurarse de que devuelve la ruta CSV (corregido en main.py también)
        assert result == "/mock/data/usuario.csv"

    def test_elegir_almacenamiento_json_default(self):
        self.mocks['Prompt'].ask.return_value = "2" # JSON

        result = main.elegir_almacenamiento()
        self.mocks['console'].print.assert_any_call(Panel.fit(mock.ANY))
        # Asegurarse de que devuelve la ruta JSON (corregido en main.py también)
        assert result == "/mock/data/usuario.json"

    def test_elegir_almacenamiento2_csv(self):
        self.mocks['Prompt'].ask.return_value = "1"

        def test_elegir_almacenamiento2_csv(self):
            self.mocks['Prompt'].ask.return_value = "1"  # CSV

            result = main.elegir_almacenamiento2()
            self.mocks['console'].print.assert_any_call(Panel.fit(mock.ANY))
            assert result == "/mock/data/libro.csv"

        def test_elegir_almacenamiento2_json_default(self):
            self.mocks['Prompt'].ask.return_value = "2"  # JSON

            result = main.elegir_almacenamiento2()
            self.mocks['console'].print.assert_any_call(Panel.fit(mock.ANY))
            assert result == "/mock/data/libro.json"