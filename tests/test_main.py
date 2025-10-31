import pytest
import os
from unittest import mock
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Importamos el módulo principal de nuestra aplicación.
# Asumimos que 'main.py' es accesible para importar.
import main

# --- Fixtures esenciales para las pruebas de UI/Coordinación ---

@pytest.fixture
def mock_console_print():
    """
    Mockea 'rich.console.Console.print'.
    Nos permite comprobar qué mensajes la aplicación intenta mostrar.
    """
    with mock.patch('main.console.print') as mock_print:
        yield mock_print

@pytest.fixture
def mock_prompt_ask():
    """
    Mockea 'rich.prompt.Prompt.ask'.
    Simula la entrada de texto del usuario.
    """
    with mock.patch('main.Prompt.ask') as mock_ask:
        yield mock_ask

@pytest.fixture
def mock_intprompt_ask():
    """
    Mockea 'rich.prompt.IntPrompt.ask'.
    Simula la entrada de números enteros del usuario.
    """
    with mock.patch('main.IntPrompt.ask') as mock_int_ask:
        yield mock_int_ask

@pytest.fixture
def mock_confirm_ask():
    """
    Mockea 'rich.prompt.Confirm.ask'.
    Simula las respuestas 'True'/'False' a preguntas de confirmación.
    """
    with mock.patch('main.Confirm.ask') as mock_confirm_ask:
        yield mock_confirm_ask

@pytest.fixture
def mock_usuario_module():
    """
    Mockea el módulo 'usuario'.
    Esto aísla 'main.py' de la lógica real de 'usuario.py'.
    Controlamos qué devuelven sus funciones y si son llamadas correctamente.
    """
    with mock.patch('main.usuario') as mock_user_mod:
        yield mock_user_mod

@pytest.fixture
def mock_libro_module():
    """
    Mockea el módulo 'libro'.
    Similar al mock de 'usuario', para aislar la lógica de libros.
    """
    with mock.patch('main.libro') as mock_book_mod:
        yield mock_book_mod

@pytest.fixture
def mock_os_path_join():
    """
    Mockea 'os.path.join' para evitar crear rutas de archivo reales
    cuando 'elegir_almacenamiento' se llama.
    Simplemente devolverá un string representativo.
    """
    with mock.patch('os.path.join') as mock_path_join:
        # Hacemos que siempre devuelva una ruta de ejemplo para la prueba.
        # Podrías ajustarlo para que devuelva algo más específico si es necesario.
        mock_path_join.side_effect = lambda dir, file: f"/mock/path/{file}"
        yield mock_path_join

# --- Pruebas para las funciones de GESTIÓN DE CLIENTES ---

def test_menu_crear_cliente_exitoso(mock_console_print, mock_intprompt_ask, mock_prompt_ask,
                                     mock_usuario_module, mock_os_path_join):
    """
    Prueba que el menú de crear cliente guía al usuario correctamente,
    recoge los datos y llama a 'usuario.crear_cliente' con éxito.
    """
    # 1. Preparación: Definimos cómo responderán los mocks a las llamadas.
    mock_intprompt_ask.return_value = 12345  # Simula el número de documento.
    mock_prompt_ask.side_effect = ["Juan", "Perez", "juan.perez@example.com"] # Nombres, Apellidos, Email.

    # Simula que 'usuario.crear_cliente' devuelve un cliente con un ID, indicando éxito.
    mock_usuario_module.crear_cliente.return_value = {
        'id': 'cli-001', 'documento': '12345', 'nombres': 'Juan',
        'apellidos': 'Perez', 'email': 'juan.perez@example.com'
    }

    # Asumimos una ruta ficticia para el archivo de datos.
    # En una prueba real, esta ruta no se usará por los mocks de usuario.
    test_filepath = "/mock/path/usuario.json"

    # 2. Ejecución: Llamamos a la función que estamos probando.
    main.menu_crear_cliente(test_filepath)

    # 3. Verificación (Asersiones): Comprobamos que las interacciones fueron las esperadas.
    mock_intprompt_ask.assert_called_once_with("Número de Documento")
    # Verificamos que Prompt.ask fue llamado para los 3 campos de texto.
    assert mock_prompt_ask.call_args_list[0].args[0] == "Nombres"
    assert mock_prompt_ask.call_args_list[1].args[0] == "Apellidos"
    assert mock_prompt_ask.call_args_list[2].args[0] == "Email"

    # Verificamos que 'usuario.crear_cliente' fue llamado con los datos recopilados.
    mock_usuario_module.crear_cliente.assert_called_once_with(
        test_filepath, 12345, "Juan", "Perez", "juan.perez@example.com"
    )
    # Verificamos que se imprimió el mensaje de éxito.
    mock_console_print.assert_any_call(
        Panel(f"✅ ¡Usuario registrado con éxito!\n   ID Asignado: [bold yellow]{'cli-001'}[/bold yellow]",
              border_style="green", title="Éxito")
    )

def test_menu_crear_cliente_fallido(mock_console_print, mock_intprompt_ask, mock_prompt_ask,
                                     mock_usuario_module, mock_os_path_join):
    """
    Prueba que el menú de crear cliente maneja un fallo
    cuando 'usuario.crear_cliente' no puede registrar al usuario.
    """
    # 1. Preparación
    mock_intprompt_ask.return_value = 12345
    mock_prompt_ask.side_effect = ["Juan", "Perez", "juan.perez@example.com"]
    # Simula que 'crear_cliente' devuelve None, indicando un fallo.
    mock_usuario_module.crear_cliente.return_value = None
    test_filepath = "/mock/path/usuario.json"

    # 2. Ejecución
    main.menu_crear_cliente(test_filepath)

    # 3. Verificación
    mock_usuario_module.crear_cliente.assert_called_once()
    mock_console_print.assert_any_call(
        Panel("⚠️ No se pudo registrar al Usuario. Verifique los datos.",
              border_style="red", title="Error")
    )


def test_menu_leer_clientes_con_datos(mock_console_print, mock_usuario_module, mock_os_path_join):
    """
    Prueba que el menú de leer clientes muestra una tabla
    cuando 'usuario.leer_todos_los_clientes' devuelve datos.
    """
    # 1. Preparación
    mock_clientes = [
        {'id': '2', 'documento': '98765', 'nombres': 'Ana', 'apellidos': 'Gomez', 'email': 'ana.gomez@example.com'},
        {'id': '1', 'documento': '12345', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan.perez@example.com'}
    ]
    mock_usuario_module.leer_todos_los_clientes.return_value = mock_clientes
    test_filepath = "/mock/path/usuario.json"

    # 2. Ejecución
    main.menu_leer_clientes(test_filepath)

    # 3. Verificación
    mock_usuario_module.leer_todos_los_clientes.assert_called_once_with(test_filepath)
    # Verificamos que se imprime el panel de título y luego se imprime una tabla.
    mock_console_print.assert_any_call(Panel.fit("[bold cyan]👥 Lista de usuarios[/bold cyan]"))
    assert any(isinstance(call.args[0], Table) for call in mock_console_print.call_args_list)


def test_menu_leer_clientes_sin_datos(mock_console_print, mock_usuario_module, mock_os_path_join):
    """
    Prueba que el menú de leer clientes muestra un mensaje
    cuando no hay usuarios registrados.
    """
    # 1. Preparación
    mock_usuario_module.leer_todos_los_clientes.return_value = []
    test_filepath = "/mock/path/usuario.json"

    # 2. Ejecución
    main.menu_leer_clientes(test_filepath)

    # 3. Verificación
    mock_usuario_module.leer_todos_los_clientes.assert_called_once_with(test_filepath)
    mock_console_print.assert_any_call("[yellow]No hay usuarios registrados.[/yellow]")


def test_menu_actualizar_cliente_exitoso(mock_console_print, mock_intprompt_ask, mock_prompt_ask,
                                         mock_usuario_module, mock_os_path_join):
    """
    Prueba la actualización exitosa de los datos de un cliente.
    """
    # 1. Preparación
    mock_intprompt_ask.return_value = 12345
    mock_usuario_module.buscar_cliente_por_documento.return_value = {
        'id': 'cli-001', 'documento': '12345', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan.perez@example.com'
    }
    # Simula que el usuario solo cambia el email.
    mock_prompt_ask.side_effect = [
        "Juan", # Nombres: no se cambia (default)
        "Perez", # Apellidos: no se cambia (default)
        "juan.nuevo@example.com" # Email: se cambia
    ]
    mock_usuario_module.actualizar_cliente.return_value = True
    test_filepath = "/mock/path/usuario.json"

    # 2. Ejecución
    main.menu_actualizar_cliente(test_filepath)

    # 3. Verificación
    mock_usuario_module.buscar_cliente_por_documento.assert_called_once_with(test_filepath, "12345")
    mock_usuario_module.actualizar_cliente.assert_called_once_with(
        test_filepath, "12345", {'email': 'juan.nuevo@example.com'}
    )
    mock_console_print.assert_any_call(
        Panel("✅ ¡Datos del usuario actualizados con éxito!", border_style="green", title="Éxito")
    )


def test_menu_actualizar_cliente_no_encontrado(mock_console_print, mock_intprompt_ask,
                                              mock_usuario_module, mock_os_path_join):
    """
    Prueba que se maneja correctamente el intento de actualizar un cliente no existente.
    """
    # 1. Preparación
    mock_intprompt_ask.return_value = 99999
    mock_usuario_module.buscar_cliente_por_documento.return_value = None
    test_filepath = "/mock/path/usuario.json"

    # 2. Ejecución
    main.menu_actualizar_cliente(test_filepath)

    # 3. Verificación
    mock_usuario_module.buscar_cliente_por_documento.assert_called_once_with(test_filepath, "99999")
    mock_console_print.assert_any_call("\n[bold red]❌ No se encontró ningún usuario con ese documento.[/bold red]")
    mock_usuario_module.actualizar_cliente.assert_not_called() # No debería llamarse a actualizar


def test_menu_actualizar_cliente_sin_cambios(mock_console_print, mock_intprompt_ask, mock_prompt_ask,
                                             mock_usuario_module, mock_os_path_join):
    """
    Prueba que se informa al usuario si no se hicieron cambios durante la actualización.
    """
    # 1. Preparación
    mock_intprompt_ask.return_value = 12345
    mock_usuario_module.buscar_cliente_por_documento.return_value = {
        'id': 'cli-001', 'documento': '12345', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan.perez@example.com'
    }
    # El usuario presiona Enter para todos los campos, sin hacer cambios.
    mock_prompt_ask.side_effect = [
        "Juan",
        "Perez",
        "juan.perez@example.com"
    ]
    test_filepath = "/mock/path/usuario.json"

    # 2. Ejecución
    main.menu_actualizar_cliente(test_filepath)

    # 3. Verificación
    mock_usuario_module.buscar_cliente_por_documento.assert_called_once_with(test_filepath, "12345")
    mock_console_print.assert_any_call("\n[yellow]No se modificó ningún dato.[/yellow]")
    mock_usuario_module.actualizar_cliente.assert_not_called()


def test_menu_eliminar_cliente_confirmado(mock_console_print, mock_intprompt_ask, mock_confirm_ask,
                                          mock_usuario_module, mock_os_path_join):
    """
    Prueba la eliminación exitosa de un cliente cuando se confirma.
    """
    # 1. Preparación
    mock_intprompt_ask.return_value = 12345
    mock_usuario_module.buscar_cliente_por_documento.return_value = {
        'id': 'cli-001', 'documento': '12345', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan.perez@example.com'
    }
    mock_confirm_ask.return_value = True # El usuario confirma
    mock_usuario_module.eliminar_cliente.return_value = True # Eliminación exitosa
    test_filepath = "/mock/path/usuario.json"

    # 2. Ejecución
    main.menu_eliminar_cliente(test_filepath)

    # 3. Verificación
    mock_usuario_module.buscar_cliente_por_documento.assert_called_once_with(test_filepath, "12345")
    mock_confirm_ask.assert_called_once()
    mock_usuario_module.eliminar_cliente.assert_called_once_with(test_filepath, "12345")
    mock_console_print.assert_any_call(
        Panel("✅ ¡Usuario eliminado con éxito!", border_style="green", title="Éxito")
    )


def test_menu_eliminar_cliente_cancelado(mock_console_print, mock_intprompt_ask, mock_confirm_ask,
                                         mock_usuario_module, mock_os_path_join):
    """
    Prueba que la eliminación de un cliente se cancela si el usuario no confirma.
    """
    # 1. Preparación
    mock_intprompt_ask.return_value = 12345
    mock_usuario_module.buscar_cliente_por_documento.return_value = {
        'id': 'cli-001', 'documento': '12345', 'nombres': 'Juan', 'apellidos': 'Perez', 'email': 'juan.perez@example.com'
    }
    mock_confirm_ask.return_value = False # El usuario cancela
    test_filepath = "/mock/path/usuario.json"

    # 2. Ejecución
    main.menu_eliminar_cliente(test_filepath)

    # 3. Verificación
    mock_usuario_module.buscar_cliente_por_documento.assert_called_once_with(test_filepath, "12345")
    mock_confirm_ask.assert_called_once()
    mock_usuario_module.eliminar_cliente.assert_not_called() # No se llama a eliminar
    mock_console_print.assert_any_call("\n[yellow]Operación cancelada.[/yellow]")


def test_menu_eliminar_cliente_no_encontrado(mock_console_print, mock_intprompt_ask,
                                             mock_usuario_module, mock_os_path_join):
    """
    Prueba que se maneja correctamente el intento de eliminar un cliente no existente.
    """
    # 1. Preparación
    mock_intprompt_ask.return_value = 99999
    mock_usuario_module.buscar_cliente_por_documento.return_value = None
    test_filepath = "/mock/path/usuario.json"

    # 2. Ejecución
    main.menu_eliminar_cliente(test_filepath)

    # 3. Verificación
    mock_usuario_module.buscar_cliente_por_documento.assert_called_once_with(test_filepath, "99999")
    mock_console_print.assert_any_call("\n[bold red]❌ No se encontró ningún usuario con ese documento.[/bold red]")
    mock_usuario_module.eliminar_cliente.assert_not_called()


# --- Pruebas para las funciones de GESTIÓN DE PRODUCTOS (LIBROS) ---

def test_menu_crear_producto_exitoso(mock_console_print, mock_intprompt_ask, mock_prompt_ask,
                                     mock_libro_module, mock_os_path_join):
    """
    Prueba la creación exitosa de un nuevo libro.
    """
    # 1. Preparación
    mock_intprompt_ask.side_effect = [9781234567890, 5]  # ISBN y Stock
    mock_prompt_ask.side_effect = ["El Gran Gatsby", "F. Scott Fitzgerald"] # Nombre y Autor

    mock_libro_module.crear_producto.return_value = {
        'id': 'lib-001', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5
    }
    test_filepath = "/mock/path/libro.json"

    # 2. Ejecución
    main.menu_crear_producto(test_filepath)

    # 3. Verificación
    assert mock_intprompt_ask.call_args_list[0].args[0] == "ISBN"
    assert mock_prompt_ask.call_args_list[0].args[0] == "Nombre"
    assert mock_prompt_ask.call_args_list[1].args[0] == "Autor"
    assert mock_intprompt_ask.call_args_list[1].args[0] == "Stock"

    mock_libro_module.crear_producto.assert_called_once_with(
        test_filepath, 9781234567890, "El Gran Gatsby", "F. Scott Fitzgerald", 5
    )
    mock_console_print.assert_any_call(
        Panel(f"✅ ¡Libro registrado con éxito!\n   ID Asignado: [bold yellow]{'lib-001'}[/bold yellow]",
              border_style="green", title="Éxito")
    )


def test_menu_crear_producto_fallido(mock_console_print, mock_intprompt_ask, mock_prompt_ask,
                                     mock_libro_module, mock_os_path_join):
    """
    Prueba que el menú de crear libro maneja un fallo en el registro.
    """
    # 1. Preparación
    mock_intprompt_ask.side_effect = [9781234567890, 5]
    mock_prompt_ask.side_effect = ["El Gran Gatsby", "F. Scott Fitzgerald"]
    mock_libro_module.crear_producto.return_value = None
    test_filepath = "/mock/path/libro.json"

    # 2. Ejecución
    main.menu_crear_producto(test_filepath)

    # 3. Verificación
    mock_libro_module.crear_producto.assert_called_once()
    mock_console_print.assert_any_call(
        Panel("⚠️ No se pudo registrar el libro. Verifique los datos.",
              border_style="red", title="Error")
    )


def test_menu_leer_productos_con_datos(mock_console_print, mock_libro_module, mock_os_path_join):
    """
    Prueba que el menú de leer libros muestra una tabla con los libros.
    """
    # 1. Preparación
    mock_productos = [
        {'id': 'lib-002', 'ISBN': '9780123456789', 'nombre': '1984', 'autor': 'George Orwell', 'stock': 3},
        {'id': 'lib-001', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5}
    ]
    mock_libro_module.leer_todos_los_productos.return_value = mock_productos
    test_filepath = "/mock/path/libro.json"

    # 2. Ejecución
    main.menu_leer_productos(test_filepath)

    # 3. Verificación
    mock_libro_module.leer_todos_los_productos.assert_called_once_with(test_filepath)
    mock_console_print.assert_any_call(Panel.fit("[bold cyan]📦 Lista de libro[/bold cyan]"))
    assert any(isinstance(call.args[0], Table) for call in mock_console_print.call_args_list)


def test_menu_leer_productos_sin_datos(mock_console_print, mock_libro_module, mock_os_path_join):
    """
    Prueba que el menú de leer libros muestra un mensaje si no hay libros.
    """
    # 1. Preparación
    mock_libro_module.leer_todos_los_productos.return_value = []
    test_filepath = "/mock/path/libro.json"

    # 2. Ejecución
    main.menu_leer_productos(test_filepath)

    # 3. Verificación
    mock_libro_print.assert_any_call("[yellow]No hay productos registrados.[/yellow]")
    mock_libro_module.leer_todos_los_productos.assert_called_once_with(test_filepath)


def test_menu_actualizar_producto_exitoso(mock_console_print, mock_intprompt_ask, mock_prompt_ask,
                                         mock_libro_module, mock_os_path_join):
    """
    Prueba la actualización exitosa de los datos de un libro.
    """
    # 1. Preparación
    mock_intprompt_ask.side_effect = [9781234567890, 10]  # ISBN y nuevo Stock
    mock_libro_module.buscar_producto_por_isdn.return_value = {
        'id': 'lib-001', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5
    }
    # Solo el stock cambia, nombre y autor se dejan por defecto.
    mock_prompt_ask.side_effect = [
        "El Gran Gatsby",
        "F. Scott Fitzgerald"
    ]
    mock_libro_module.actualizar_producto.return_value = True
    test_filepath = "/mock/path/libro.json"

    # 2. Ejecución
    main.menu_actualizar_producto(test_filepath)

    # 3. Verificación
    mock_libro_module.buscar_producto_por_isdn.assert_called_once_with(test_filepath, "9781234567890")
    mock_libro_module.actualizar_producto.assert_called_once_with(
        test_filepath, "9781234567890", {'stock': 10}
    )
    mock_console_print.assert_any_call(
        Panel("✅ ¡Datos del libro actualizados con éxito!", border_style="green", title="Éxito")
    )


def test_menu_actualizar_producto_no_encontrado(mock_console_print, mock_intprompt_ask,
                                              mock_libro_module, mock_os_path_join):
    """
    Prueba que se maneja el intento de actualizar un libro no existente.
    """
    # 1. Preparación
    mock_intprompt_ask.return_value = 9999999999999
    mock_libro_module.buscar_producto_por_isdn.return_value = None
    test_filepath = "/mock/path/libro.json"

    # 2. Ejecución
    main.menu_actualizar_producto(test_filepath)

    # 3. Verificación
    mock_libro_module.buscar_producto_por_isdn.assert_called_once_with(test_filepath, "9999999999999")
    mock_console_print.assert_any_call("\n[bold red]❌ No se encontró ningún producto con ese ISBN.[/bold red]")
    mock_libro_module.actualizar_producto.assert_not_called()


def test_menu_actualizar_producto_sin_cambios(mock_console_print, mock_intprompt_ask, mock_prompt_ask,
                                             mock_libro_module, mock_os_path_join):
    """
    Prueba que se informa si no se realizaron cambios durante la actualización del libro.
    """
    # 1. Preparación
    mock_intprompt_ask.side_effect = [9781234567890, 5]
    mock_libro_module.buscar_producto_por_isdn.return_value = {
        'id': 'lib-001', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5
    }
    # No se hacen cambios en los prompts de texto o en el IntPrompt de stock
    mock_prompt_ask.side_effect = [
        "El Gran Gatsby",
        "F. Scott Fitzgerald"
    ]
    test_filepath = "/mock/path/libro.json"

    # 2. Ejecución
    main.menu_actualizar_producto(test_filepath)

    # 3. Verificación
    mock_libro_module.buscar_producto_por_isdn.assert_called_once_with(test_filepath, "9781234567890")
    mock_console_print.assert_any_call("\n[yellow]No se modificó ningún dato.[/yellow]")
    mock_libro_module.actualizar_producto.assert_not_called()


def test_menu_eliminar_producto_confirmado(mock_console_print, mock_intprompt_ask, mock_confirm_ask,
                                          mock_libro_module, mock_os_path_join):
    """
    Prueba la eliminación exitosa de un libro cuando se confirma.
    """
    # 1. Preparación
    mock_intprompt_ask.return_value = 9781234567890
    mock_libro_module.buscar_producto_por_isdn.return_value = {
        'id': 'lib-001', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5
    }
    mock_confirm_ask.return_value = True # El usuario confirma
    mock_libro_module.eliminar_producto.return_value = True # Eliminación exitosa
    test_filepath = "/mock/path/libro.json"

    # 2. Ejecución
    main.menu_eliminar_producto(test_filepath)

    # 3. Verificación
    mock_libro_module.buscar_producto_por_isdn.assert_called_once_with(test_filepath, "9781234567890")
    mock_confirm_ask.assert_called_once()
    mock_libro_module.eliminar_producto.assert_called_once_with(test_filepath, "9781234567890")
    mock_console_print.assert_any_call(
        Panel("✅ ¡Libro eliminado con éxito!", border_style="green", title="Éxito")
    )


def test_menu_eliminar_producto_cancelado(mock_console_print, mock_intprompt_ask, mock_confirm_ask,
                                         mock_libro_module, mock_os_path_join):
    """
    Prueba que la eliminación de un libro se cancela si el usuario no confirma.
    """
    # 1. Preparación
    mock_intprompt_ask.return_value = 9781234567890
    mock_libro_module.buscar_producto_por_isdn.return_value = {
        'id': 'lib-001', 'ISBN': '9781234567890', 'nombre': 'El Gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'stock': 5
    }
    mock_confirm_ask.return_value = False # El usuario cancela
    test_filepath = "/mock/path/libro.json"

    # 2. Ejecución
    main.menu_eliminar_producto(test_filepath)

    # 3. Verificación
    mock_libro_module.buscar_producto_por_isdn.assert_called_once_with(test