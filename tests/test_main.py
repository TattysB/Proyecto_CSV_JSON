import os
import sys
from unittest import mock
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box


# Asegurarse de que el directorio raíz del proyecto esté en sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar 'main' como un módulo estándar.
import main

# Importar Rich aquí para poder parchear sus componentes directamente
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table



class BaseTestWithMocks:
    """Clase base para pruebas que necesitan mocks comunes."""

    def setup_method(self):
        """Prepara los mocks antes de cada prueba."""
        # Se parchean los componentes de Rich directamente desde sus módulos originales
        self.patcher_rich_components = mock.patch.multiple(
            'rich.prompt',
            Prompt=mock.DEFAULT,
            IntPrompt=mock.DEFAULT,
            Confirm=mock.DEFAULT,
        )
        self.patcher_console = mock.patch('main.console', spec=Console) # Se parcha la instancia de console en main

        # CORRECTO: Parchear los módulos de lógica de negocio como atributos de 'main'
        self.patcher_main_modules_and_constants = mock.patch.multiple(
            main,
            usuario=mock.DEFAULT,    # Se accederá como main.usuario
            libro=mock.DEFAULT,      # Se accederá como main.libro
            prestamos=mock.DEFAULT,  # Se accederá como main.prestamos
            ARCHIVO_USUARIOS_CSV=mock.DEFAULT,
            ARCHIVO_USUARIOS_JSON=mock.DEFAULT,
            ARCHIVO_LIBROS_CSV=mock.DEFAULT,
            ARCHIVO_LIBROS_JSON=mock.DEFAULT,
            ARCHIVO_PRESTAMOS_CSV=mock.DEFAULT,
            ARCHIVO_PRESTAMOS_JSON=mock.DEFAULT,
            DIRECTORIO_DATOS=mock.DEFAULT,
            BASE_DIR=mock.DEFAULT,
        )


        # Se inicializan todos los parcheos
        self.mocks = {}
        self.mocks.update(self.patcher_rich_components.start())
        self.mocks['console'] = self.patcher_console.start()
        self.mocks.update(self.patcher_main_modules_and_constants.start())


        # Aseguramos que el método .print de la consola mockeada también sea un mock.Mock
        self.mocks['console'].print = mock.Mock()

        # Configurar los mocks para las CONSTANTES REALES de main.py
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
        self.patcher_console.stop()
        self.patcher_main_modules_and_constants.stop()
        self._os_path_join_patcher.stop()
        self._os_makedirs_patcher.stop()
        self._os_path_exists_patcher.stop()
        self.mocks = {}

    def _mock_os_path_join_side_effect(self, dir_path: str, file_name: str) -> str:
        """Side effect para mockear os.path.join consistentemente."""
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
        # Esto es para el caso de menu_crear_prestamo que construye rutas usando BASE_DIR
        # y los nombres de archivo directamente.
        elif dir_path == self.mocks['BASE_DIR'] and file_name in [
            "prestamo.json", "usuario.json", "libro.json"
        ]:
            return f"{self.mocks['BASE_DIR']}/{file_name}"

        # Este es un caso especial para `menu_listar_prestamo` y `menu_listar_devoluciones_prestamos`
        # que usan rutas relativas como os.path.join("directorio", "data", "prestamo.json")
        elif dir_path == "directorio" and file_name == "data":
            return f"{dir_path}/{file_name}" # Retorna "directorio/data"
        elif dir_path == "directorio/data" and file_name in [
            "prestamo.json", "usuario.json", "libro.json"
        ]:
            return f"directorio/data/{file_name}"


        return os.path.join(dir_path, file_name) # Fallback para comportamiento normal si no hay mock específico


class TestUsuarios(BaseTestWithMocks):

    def test_menu_crear_usuario_exitoso(self):
        test_filepath = "/mock/data/usuario.json"

        self.mocks['IntPrompt'].ask.return_value = 123
        self.mocks['Prompt'].ask.side_effect = ["Juan", "Perez", "juan@example.com"]
        self.mocks['usuario'].crear_usuario.return_value = {'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'}

        main.menu_crear_usuario(test_filepath)

        self.mocks['IntPrompt'].ask.assert_called_once_with("Número de Documento")
        assert self.mocks['Prompt'].ask.call_args_list[0].args[0] == "Nombres"
        assert self.mocks['Prompt'].ask.call_args_list[1].args[0] == "Apellidos"
        assert self.mocks['Prompt'].ask.call_args_list[2].args[0] == "Email"
        self.mocks['usuario'].crear_usuario.assert_called_once_with(test_filepath, 123, "Juan", "Perez", "juan@example.com")
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="green", title="Éxito"))

    def test_menu_leer_usuario_con_datos(self):
        test_filepath = "/mock/data/usuario.json"

        self.mocks['usuario'].leer_todos_los_usuario.return_value = [{'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'}]

        main.menu_leer_usuario(test_filepath)

        self.mocks['usuario'].leer_todos_los_usuario.assert_called_once_with(test_filepath)
        assert any(isinstance(call.args[0], Table) for call in self.mocks['console'].print.call_args_list)

    def test_menu_actualizar_usuario_exitoso(self):
        test_filepath = "/mock/data/usuario.json"

        self.mocks['IntPrompt'].ask.return_value = 123
        self.mocks['usuario'].buscar_usuario_por_documento.return_value = {'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'}
        self.mocks['Prompt'].ask.side_effect = ["Juan", "Perez", "nuevo.juan@example.com"]
        self.mocks['usuario'].actualizar_usuario.return_value = True

        main.menu_actualizar_usuario(test_filepath)

        self.mocks['usuario'].buscar_usuario_por_documento.assert_called_once_with(test_filepath, "123")
        self.mocks['usuario'].actualizar_usuario.assert_called_once_with(test_filepath, "123", {'email': 'nuevo.juan@example.com'})
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Datos del usuario actualizados con éxito!", border_style="green", title="Éxito"))

    def test_menu_eliminar_usuario_confirmado(self):
        test_filepath = "/mock/data/usuario.json"

        self.mocks['IntPrompt'].ask.return_value = 123
        self.mocks['usuario'].buscar_usuario_por_documento.return_value = {'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'}
        self.mocks['Confirm'].ask.return_value = True
        self.mocks['usuario'].eliminar_usuario.return_value = True

        main.menu_eliminar_usuario(test_filepath)

        self.mocks['usuario'].buscar_usuario_por_documento.assert_called_once_with(test_filepath, "123")
        self.mocks['Confirm'].ask.assert_called_once()
        self.mocks['usuario'].eliminar_usuario.assert_called_once_with(test_filepath, "123")
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Usuario eliminado con éxito!", border_style="green", title="Éxito"))


class TestLibros(BaseTestWithMocks):

    def test_menu_crear_libro_exitoso(self):
        test_filepath = "/mock/data/libro.json"

        self.mocks['IntPrompt'].ask.side_effect = [9781234567890, 5]
        self.mocks['Prompt'].ask.side_effect = ["El Gran Gatsby", "F. Scott Fitzgerald"]
        self.mocks['libro'].crear_libro.return_value = {'id': '1', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5}

        main.menu_crear_libro(test_filepath)

        assert self.mocks['IntPrompt'].ask.call_args_list[0].args[0] == "ISBN"
        assert self.mocks['Prompt'].ask.call_args_list[0].args[0] == "Nombre"
        assert self.mocks['Prompt'].ask.call_args_list[1].args[0] == "Autor"
        assert self.mocks['IntPrompt'].ask.call_args_list[1].args[0] == "Stock"
        self.mocks['libro'].crear_libro.assert_called_once_with(test_filepath, 9781234567890, "El Gran Gatsby", "F. Scott Fitzgerald", 5)
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="green", title="Éxito"))

    def test_menu_leer_libros_con_datos(self):
        test_filepath = "/mock/data/libro.json"

        self.mocks['libro'].leer_todos_los_libros.return_value = [{'id': '1', 'ISBN': '978123', 'nombre': 'Libro Test', 'autor': 'Autor Test', 'stock': 10}]

        main.menu_leer_libros(test_filepath)

        self.mocks['libro'].leer_todos_los_libros.assert_called_once_with(test_filepath)
        assert any(isinstance(call.args[0], Table) for call in self.mocks['console'].print.call_args_list)

    def test_menu_actualizar_libro_exitoso(self):
        test_filepath = "/mock/data/libro.json"

        self.mocks['IntPrompt'].ask.side_effect = [9781234567890, 10]
        self.mocks['libro'].buscar_libro_por_isbn.return_value = {'id': '1', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5}
        self.mocks['Prompt'].ask.side_effect = ["El Gran Gatsby", "F. Scott Fitzgerald"]
        self.mocks['libro'].actualizar_libro.return_value = True

        main.menu_actualizar_libro(test_filepath)

        self.mocks['libro'].buscar_libro_por_isbn.assert_called_once_with(test_filepath, "9781234567890")
        self.mocks['libro'].actualizar_libro.assert_called_once_with(test_filepath, "9781234567890", {'stock': 10})
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Datos del libro actualizados con éxito!", border_style="green", title="Éxito"))

    def test_menu_eliminar_libro_confirmado(self):
        test_filepath = "/mock/data/libro.json"

        self.mocks['IntPrompt'].ask.return_value = 9781234567890
        self.mocks['libro'].buscar_libro_por_isbn.return_value = {'id': '1', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5}
        self.mocks['Confirm'].ask.return_value = True
        self.mocks['libro'].eliminar_libro.return_value = True

        main.menu_eliminar_libro(test_filepath)

        self.mocks['libro'].buscar_libro_por_isbn.assert_called_once_with(test_filepath, "9781234567890")
        self.mocks['Confirm'].ask.assert_called_once()
        self.mocks['libro'].eliminar_libro.assert_called_once_with(test_filepath, "9781234567890")
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Libro eliminado con éxito!", border_style="green", title="Éxito"))


class TestPrestamos(BaseTestWithMocks):

    def test_menu_crear_prestamo_exitoso(self):
        self.mocks['Prompt'].ask.side_effect = ["user123", "book456"]
        self.mocks['prestamos'].realizar_prestamo.return_value = {'id_prestamo': 'P001', 'id_usuario': 'user123', 'id_libro': 'book456'}

        # Se pasa un filepath dummy porque la función `menu_crear_prestamo` en main.py
        # construye sus propias rutas a los archivos de datos para `realizar_prestamo`.
        # Estas rutas dependen de las constantes ARCHIVO_PRESTAMOS_JSON, etc.,
        # y de BASE_DIR/DIRECTORIO_DATOS, que ya están siendo mockeadas.
        main.menu_crear_prestamo("/mock/data/dummy.json")

        self.mocks['Prompt'].ask.call_args_list[0].args[0] == "ID del usuario"
        self.mocks['Prompt'].ask.call_args_list[1].args[0] == "ID del libro"
        self.mocks['prestamos'].realizar_prestamo.assert_called_once_with(
            f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_PRESTAMOS_JSON']}",
            f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_USUARIOS_JSON']}",
            f"{self.mocks['DIRECTORIO_DATOS']}/{self.mocks['ARCHIVO_LIBROS_JSON']}",
            "user123", "book456"
        )
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="green", title="Éxito"))


    def test_menu_registrar_devolucion_exitoso(self):
        test_filepath_prestamos = "/mock/data/prestamo.json"
        test_filepath_libros = "/mock/data/libro.json"

        self.mocks['Prompt'].ask.return_value = "P001"
        self.mocks['prestamos'].registrar_devolucion.return_value = {'id_prestamo': 'P001', 'estado': 'devuelto'}

        main.menu_registrar_devolucion(test_filepath_prestamos, test_filepath_libros)

        self.mocks['Prompt'].ask.assert_called_once_with("id_prestamo")
        self.mocks['prestamos'].registrar_devolucion.assert_called_once_with(
            test_filepath_prestamos,
            test_filepath_libros,
            "P001"
        )
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="green", title="Éxito"))

    def test_menu_listar_prestamo_con_datos(self):
        test_filepath = "/mock/data/prestamo.json"
        self.mocks['prestamos'].listar_prestamos.return_value = [
            {'id_prestamo': 'P001', 'usuario': 'Juan Perez', 'libro': 'El Gran Gatsby',
             'fecha_prestamo': '2023-01-01', 'fecha_devolucion_esperada': '2023-01-15', 'estado': 'prestado'}
        ]

        main.menu_listar_prestamo(test_filepath)

        self.mocks['prestamos'].listar_prestamos.assert_called_once_with(
            os.path.join("directorio", "data", "prestamo.json"),
            os.path.join("directorio", "data", "usuario.json"),
            os.path.join("directorio", "data", "libro.json")
        )
        assert any(isinstance(call.args[0], Table) for call in self.mocks['console'].print.call_args_list)

    def test_menu_listar_devoluciones_prestamos_con_datos(self):
        self.mocks['prestamos'].listar_devoluciones.return_value = [
            {'id_prestamo': 'P001', 'usuario': 'Juan Perez', 'libro': 'El Gran Gatsby',
             'fecha_prestamo': '2023-01-01', 'fecha_devolucion_esperada': '2023-01-15', 'estado': 'devuelto'}
        ]

        main.menu_listar_devoluciones_prestamos()

        self.mocks['prestamos'].listar_devoluciones.assert_called_once_with(
            os.path.join("directorio", "data", "prestamo.json"),
            os.path.join("directorio", "data", "usuario.json"),
            os.path.join("directorio", "data", "libro.json")
        )
        assert any(isinstance(call.args[0], Table) for call in self.mocks['console'].print.call_args_list)


class TestMainLogic(BaseTestWithMocks):

    def test_main_exit_option(self):
        self.mocks['Prompt'].ask.side_effect = ["4"]

        main.main()

        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="bright_magenta", box=box.DOUBLE_EDGE))

    def test_main_access_client_menu_and_exit(self):
        self.mocks['Prompt'].ask.side_effect = ["1", "2", "5", "4"]

        main.main()

        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="bright_magenta", box=box.DOUBLE_EDGE))

    def test_main_access_book_menu_and_exit(self):
        self.mocks['Prompt'].ask.side_effect = ["2", "2", "5", "4"]

        main.main()

        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="bright_magenta", box=box.DOUBLE_EDGE))

    def test_main_access_prestamos_menu_and_exit(self):
        self.mocks['Prompt'].ask.side_effect = ["3", "2", "5", "4"]

        main.main()

        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="bright_magenta", box=box.DOUBLE_EDGE))


    def test_elegir_almacenamiento_csv(self):
        self.mocks['Prompt'].ask.return_value = "1"

        result = main.elegir_almacenamiento()
        self.mocks['console'].print.assert_any_call(Panel.fit(mock.ANY))
        assert result == "/mock/data/usuario.csv"

    def test_elegir_almacenamiento_json_default(self):
        self.mocks['Prompt'].ask.return_value = "2"

        result = main.elegir_almacenamiento()
        self.mocks['console'].print.assert_any_call(Panel.fit(mock.ANY))
        assert result == "/mock/data/usuario.json"

    def test_elegir_almacenamiento2_csv(self):
        self.mocks['Prompt'].ask.return_value = "1"

        result = main.elegir_almacenamiento2()
        self.mocks['console'].print.assert_any_call(Panel.fit(mock.ANY))
        assert result == "/mock/data/libro.csv"

    def test_elegir_almacenamiento2_json_default(self):
        self.mocks['Prompt'].ask.return_value = "2"

        result = main.elegir_almacenamiento2()
        self.mocks['console'].print.assert_any_call(Panel.fit(mock.ANY))
        assert result == "/mock/data/libro.json"