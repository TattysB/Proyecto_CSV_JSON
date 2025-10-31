import os
import sys
from unittest import mock
from rich.panel import Panel
from rich.table import Table


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# se importa 'main' como un módulo estándar.
import main

# se importa Rich aquí para poder parchear sus componentes directamente
from rich.console import Console


class BaseTestWithMocks:
    """Clase base para pruebas que necesitan mocks comunes."""

    def setup_method(self):
        """Prepara los mocks antes de cada prueba."""
        # se archea los componentes de Rich directamente desde sus módulos originales
        # y los atributos 'usuario' y 'libro' del módulo 'main'.
        # se usa mock.DEFAULT para obtener el mock objeto.
        self.patcher_rich_components = mock.patch.multiple(
            'rich.prompt', # Módulo donde están Prompt, IntPrompt, Confirm
            Prompt=mock.DEFAULT,
            IntPrompt=mock.DEFAULT,
            Confirm=mock.DEFAULT,
        )
        self.patcher_main_modules = mock.patch.multiple(
            main, # Módulo main donde están usuario y libro importados
            usuario=mock.DEFAULT,
            libro=mock.DEFAULT,
        )
        self.patcher_console = mock.patch('main.console', spec=Console) # se parcha la instancia de console en main

        # se inicializan todos los parcheos
        self.mocks = {}
        self.mocks.update(self.patcher_rich_components.start())
        self.mocks.update(self.patcher_main_modules.start())
        self.mocks['console'] = self.patcher_console.start()

        # Aseguramos que el método .print de la consola mockeada también sea un mock.Mock
        self.mocks['console'].print = mock.Mock()

        # se parcha os.path.join para devolver rutas consistentes en las pruebas
        self._os_path_join_patcher = mock.patch(
            'os.path.join', side_effect=self._mock_os_path_join_side_effect
        )
        self.mocks['os_path_join'] = self._os_path_join_patcher.start()


    def teardown_method(self):
        """Limpia los mocks después de cada prueba."""
        self.patcher_rich_components.stop()
        self.patcher_main_modules.stop()
        self.patcher_console.stop()
        self._os_path_join_patcher.stop()
        self.mocks = {}

    def _mock_os_path_join_side_effect(self, dir_path: str, file_name: str) -> str:
        """Side effect para mockear os.path.join consistentemente."""
        if file_name == main.NOMBRE_ARCHIVO_CSV:
            return "/mock/data/usuario.csv"
        elif file_name == main.NOMBRE_ARCHIVO_JSON:
            return "/mock/data/usuario.json"
        elif file_name == main.NOMBRE_ARCHIVO_CSV2:
            return "/mock/data/libro.csv"
        elif file_name == main.NOMBRE_ARCHIVO_JSON2:
            return "/mock/data/libro.json"
        return f"/mock/data/{file_name}"


class TestClientes(BaseTestWithMocks):

    def test_menu_crear_cliente_exitoso(self):
        test_filepath = "/mock/data/usuario.json"

        self.mocks['IntPrompt'].ask.return_value = 123
        self.mocks['Prompt'].ask.side_effect = ["Juan", "Perez", "juan@example.com"]
        self.mocks['usuario'].crear_cliente.return_value = {'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'}

        main.menu_crear_cliente(test_filepath)

        self.mocks['IntPrompt'].ask.assert_called_once_with("Número de Documento")
        assert self.mocks['Prompt'].ask.call_args_list[0].args[0] == "Nombres"
        assert self.mocks['Prompt'].ask.call_args_list[1].args[0] == "Apellidos"
        assert self.mocks['Prompt'].ask.call_args_list[2].args[0] == "Email"
        self.mocks['usuario'].crear_cliente.assert_called_once_with(test_filepath, 123, "Juan", "Perez", "juan@example.com")
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="green", title="Éxito"))

    def test_menu_leer_clientes_con_datos(self):
        test_filepath = "/mock/data/usuario.json"

        self.mocks['usuario'].leer_todos_los_clientes.return_value = [{'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'}]

        main.menu_leer_clientes(test_filepath)

        self.mocks['usuario'].leer_todos_los_clientes.assert_called_once_with(test_filepath)
        assert any(isinstance(call.args[0], Table) for call in self.mocks['console'].print.call_args_list)

    def test_menu_actualizar_cliente_exitoso(self):
        test_filepath = "/mock/data/usuario.json"

        self.mocks['IntPrompt'].ask.return_value = 123
        self.mocks['usuario'].buscar_cliente_por_documento.return_value = {'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'}
        self.mocks['Prompt'].ask.side_effect = ["Juan", "Perez", "nuevo.juan@example.com"]
        self.mocks['usuario'].actualizar_cliente.return_value = True

        main.menu_actualizar_cliente(test_filepath)

        self.mocks['usuario'].buscar_cliente_por_documento.assert_called_once_with(test_filepath, "123")
        self.mocks['usuario'].actualizar_cliente.assert_called_once_with(test_filepath, "123", {'email': 'nuevo.juan@example.com'})
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Datos del usuario actualizados con éxito!", border_style="green", title="Éxito"))

    def test_menu_eliminar_cliente_confirmado(self):
        test_filepath = "/mock/data/usuario.json"

        self.mocks['IntPrompt'].ask.return_value = 123
        self.mocks['usuario'].buscar_cliente_por_documento.return_value = {'id': '1', 'documento': '123', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan@example.com'}
        self.mocks['Confirm'].ask.return_value = True
        self.mocks['usuario'].eliminar_cliente.return_value = True

        main.menu_eliminar_cliente(test_filepath)

        self.mocks['usuario'].buscar_cliente_por_documento.assert_called_once_with(test_filepath, "123")
        self.mocks['Confirm'].ask.assert_called_once()
        self.mocks['usuario'].eliminar_cliente.assert_called_once_with(test_filepath, "123")
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Usuario eliminado con éxito!", border_style="green", title="Éxito"))


class TestLibros(BaseTestWithMocks):

    def test_menu_crear_producto_exitoso(self):
        test_filepath = "/mock/data/libro.json"

        self.mocks['IntPrompt'].ask.side_effect = [9781234567890, 5]
        self.mocks['Prompt'].ask.side_effect = ["El Gran Gatsby", "F. Scott Fitzgerald"]
        self.mocks['libro'].crear_producto.return_value = {'id': '1', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5}

        main.menu_crear_producto(test_filepath)

        assert self.mocks['IntPrompt'].ask.call_args_list[0].args[0] == "ISBN"
        assert self.mocks['Prompt'].ask.call_args_list[0].args[0] == "Nombre"
        assert self.mocks['Prompt'].ask.call_args_list[1].args[0] == "Autor"
        assert self.mocks['IntPrompt'].ask.call_args_list[1].args[0] == "Stock"
        self.mocks['libro'].crear_producto.assert_called_once_with(test_filepath, 9781234567890, "El Gran Gatsby", "F. Scott Fitzgerald", 5)
        self.mocks['console'].print.assert_any_call(Panel(mock.ANY, border_style="green", title="Éxito"))

    def test_menu_leer_productos_con_datos(self):
        test_filepath = "/mock/data/libro.json"

        self.mocks['libro'].leer_todos_los_productos.return_value = [{'id': '1', 'ISBN': '978123', 'nombre': 'Libro Test', 'autor': 'Autor Test', 'stock': 10}]

        main.menu_leer_productos(test_filepath)

        self.mocks['libro'].leer_todos_los_productos.assert_called_once_with(test_filepath)
        assert any(isinstance(call.args[0], Table) for call in self.mocks['console'].print.call_args_list)

    def test_menu_actualizar_producto_exitoso(self):
        test_filepath = "/mock/data/libro.json"

        self.mocks['IntPrompt'].ask.side_effect = [9781234567890, 10]
        self.mocks['libro'].buscar_producto_por_isdn.return_value = {'id': '1', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5}
        self.mocks['Prompt'].ask.side_effect = ["El Gran Gatsby", "F. Scott Fitzgerald"]
        self.mocks['libro'].actualizar_producto.return_value = True

        main.menu_actualizar_producto(test_filepath)

        self.mocks['libro'].buscar_producto_por_isdn.assert_called_once_with(test_filepath, "9781234567890")
        self.mocks['libro'].actualizar_producto.assert_called_once_with(test_filepath, "9781234567890", {'stock': 10})
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Datos del libro actualizados con éxito!", border_style="green", title="Éxito"))

    def test_menu_eliminar_producto_confirmado(self):
        test_filepath = "/mock/data/libro.json"

        self.mocks['IntPrompt'].ask.return_value = 9781234567890
        self.mocks['libro'].buscar_producto_por_isdn.return_value = {'id': '1', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5}
        self.mocks['Confirm'].ask.return_value = True
        self.mocks['libro'].eliminar_producto.return_value = True

        main.menu_eliminar_producto(test_filepath)

        self.mocks['libro'].buscar_producto_por_isdn.assert_called_once_with(test_filepath, "9781234567890")
        self.mocks['Confirm'].ask.assert_called_once()
        self.mocks['libro'].eliminar_producto.assert_called_once_with(test_filepath, "9781234567890")
        self.mocks['console'].print.assert_any_call(Panel("✅ ¡Libro eliminado con éxito!", border_style="green", title="Éxito"))


class TestMainLogic(BaseTestWithMocks):

    def test_main_exit_option(self):
        self.mocks['Prompt'].ask.side_effect = ["3"]

        main.main()

        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 ¡Hasta luego! Gracias por usar la agenda.[/bold magenta]")

    def test_main_access_client_menu_and_exit(self):
        self.mocks['Prompt'].ask.side_effect = ["1", "5", "3"]

        main.main()

        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 ¡Hasta luego! Gracias por usar la agenda.[/bold magenta]")

    def test_main_access_book_menu_and_exit(self):
        self.mocks['Prompt'].ask.side_effect = ["2", "5", "3"]

        main.main()

        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 Volviendo al menú principal...[/bold magenta]")
        self.mocks['console'].print.assert_any_call("\n[bold magenta]👋 ¡Hasta luego! Gracias por usar la agenda.[/bold magenta]")

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