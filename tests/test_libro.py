import pytest
import sys
import os

# Añade la carpeta raíz del proyecto al path de importación
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Importamos el módulo 'libro' desde la carpeta 'directorio'
from directorio.libro import (
    generar_id_prodcuto,  # se mantiene el nombre original del módulo
    crear_libro,
    leer_todos_los_libros,
    buscar_libro_por_isbn,
    actualizar_libro,
    eliminar_libro
)

# Importamos gestor_datos2 también desde la carpeta 'directorio'
from directorio import gestor_datos2

# Ruta al archivo de datos de prueba
TEST_FILEPATH = 'test_libros.json'  # Este archivo se creará en la raíz del proyecto durante las pruebas


# --- Fixtures ---

@pytest.fixture
def libros_vacios():
    """Crea un archivo de datos vacío antes de cada test."""
    if os.path.exists(TEST_FILEPATH):
        os.remove(TEST_FILEPATH)
    gestor_datos2.guardar_datos(TEST_FILEPATH, [])
    return TEST_FILEPATH


@pytest.fixture
def libros_con_datos():
    """Carga algunos datos iniciales para las pruebas."""
    if os.path.exists(TEST_FILEPATH):
        os.remove(TEST_FILEPATH)
    datos_iniciales = [
        {'id': '1', 'ISBN': '978-0321765723', 'nombre': 'El Señor de los Anillos', 'autor': 'J.R.R. Tolkien', 'stock': '10'},
        {'id': '2', 'ISBN': '978-0743273565', 'nombre': 'Cien años de soledad', 'autor': 'Gabriel García Márquez', 'stock': '5'}
    ]
    gestor_datos2.guardar_datos(TEST_FILEPATH, datos_iniciales)
    return TEST_FILEPATH


# --- Tests para generar_id_prodcuto ---

def test_generar_id_producto_lista_vacia():
    """El ID generado debe ser 1 cuando la lista de libros está vacía."""
    libros = []
    nuevo_id = generar_id_prodcuto(libros)
    assert nuevo_id == 1


def test_generar_id_producto_con_libros():
    """El ID generado debe ser el máximo actual + 1."""
    libros = [
        {'id': '1', 'ISBN': '111', 'nombre': 'Libro A', 'autor': 'Autor A', 'stock': '5'},
        {'id': '3', 'ISBN': '222', 'nombre': 'Libro B', 'autor': 'Autor B', 'stock': '10'},
        {'id': '2', 'ISBN': '333', 'nombre': 'Libro C', 'autor': 'Autor C', 'stock': '3'}
    ]
    nuevo_id = generar_id_prodcuto(libros)
    assert nuevo_id == 4


def test_generar_id_producto_id_no_entero():
    """Si los IDs no son enteros, deben tratarse como 0."""
    libros = [
        {'id': 'uno', 'ISBN': '111', 'nombre': 'Libro A', 'autor': 'Autor A', 'stock': '5'},
        {'id': '2', 'ISBN': '222', 'nombre': 'Libro B', 'autor': 'Autor B', 'stock': '10'},
    ]
    nuevo_id = generar_id_prodcuto(libros)
    assert nuevo_id == 3


# --- Tests para crear_libro ---

def test_crear_libro_exitoso(libros_vacios):
    """Se puede crear un libro nuevo correctamente."""
    filepath = libros_vacios
    libro = crear_libro(filepath, 12345, "Python Avanzado", "Ana Torres", 20)
    assert libro is not None
    assert libro['ISBN'] == '12345'
    assert libro['nombre'] == "Python Avanzado"
    assert libro['autor'] == "Ana Torres"
    assert libro['stock'] == '20'  # Se guarda como string
    libros_actualizados = gestor_datos2.cargar_datos(filepath)
    assert len(libros_actualizados) == 1
    assert libros_actualizados[0]['ISBN'] == '12345'


def test_crear_libro_existente(libros_con_datos):
    """No se puede crear un libro con un ISBN ya existente."""
    filepath = libros_con_datos
    libro_existente = crear_libro(filepath, '978-0321765723', "Otro Libro", "Otro Autor", 5)
    assert libro_existente is None
    libros_actualizados = gestor_datos2.cargar_datos(filepath)
    assert len(libros_actualizados) == 2  # No debe haber añadido un nuevo libro


def test_crear_libro_id_autoincremental(libros_con_datos):
    """El ID se genera correctamente para un nuevo libro."""
    filepath = libros_con_datos
    libro = crear_libro(filepath, '99999', "Nuevo Libro", "Nuevo Autor", 15)
    assert libro is not None
    assert libro['id'] == '3'  # Debe ser el siguiente ID disponible


# --- Tests para leer_todos_los_libros ---

def test_leer_todos_los_libros_vacios(libros_vacios):
    """Debe devolver una lista vacía si no hay libros."""
    filepath = libros_vacios
    libros = leer_todos_los_libros(filepath)
    assert isinstance(libros, list)
    assert len(libros) == 0


def test_leer_todos_los_libros_con_datos(libros_con_datos):
    """Debe devolver todos los libros existentes."""
    filepath = libros_con_datos
    libros = leer_todos_los_libros(filepath)
    assert isinstance(libros, list)
    assert len(libros) == 2
    assert libros[0]['ISBN'] == '978-0321765723'
    assert libros[1]['nombre'] == 'Cien años de soledad'


# --- Tests para buscar_libro_por_isbn ---

def test_buscar_libro_por_isbn_existente(libros_con_datos):
    """Debe encontrar un libro por su ISBN."""
    filepath = libros_con_datos
    isbn_buscado = '978-0743273565'
    libro_encontrado = buscar_libro_por_isbn(filepath, isbn_buscado)
    assert libro_encontrado is not None
    assert libro_encontrado['ISBN'] == isbn_buscado
    assert libro_encontrado['autor'] == 'Gabriel García Márquez'


def test_buscar_libro_por_isbn_no_existente(libros_con_datos):
    """No debe encontrar un libro con ISBN inexistente."""
    filepath = libros_con_datos
    isbn_no_existente = '999-9999999999'
    libro_encontrado = buscar_libro_por_isbn(filepath, isbn_no_existente)
    assert libro_encontrado is None


def test_buscar_libro_por_isbn_lista_vacia(libros_vacios):
    """No debe encontrar un libro en una lista vacía."""
    filepath = libros_vacios
    isbn_buscado = '111-2222222222'
    libro_encontrado = buscar_libro_por_isbn(filepath, isbn_buscado)
    assert libro_encontrado is None


# --- Tests para actualizar_libro ---

def test_actualizar_libro_existente(libros_con_datos):
    """Debe actualizar los datos de un libro existente."""
    filepath = libros_con_datos
    isbn_a_actualizar = '978-0321765723'
    datos_nuevos = {'nombre': 'El Señor de los Anillos: La Comunidad del Anillo', 'stock': 12}
    libro_actualizado = actualizar_libro(filepath, isbn_a_actualizar, datos_nuevos)
    assert libro_actualizado is not None
    assert libro_actualizado['nombre'] == 'El Señor de los Anillos: La Comunidad del Anillo'
    assert libro_actualizado['stock'] == '12'
    libros = gestor_datos2.cargar_datos(filepath)
    libro_verificado = next(l for l in libros if l['ISBN'] == isbn_a_actualizar)
    assert libro_verificado['nombre'] == 'El Señor de los Anillos: La Comunidad del Anillo'
    assert libro_verificado['stock'] == '12'


def test_actualizar_libro_no_existente(libros_con_datos):
    """No debe actualizar nada si el ISBN no existe."""
    filepath = libros_con_datos
    isbn_no_existente = '000-0000000000'
    datos_nuevos = {'nombre': 'Libro Inexistente', 'stock': 1}
    libro_actualizado = actualizar_libro(filepath, isbn_no_existente, datos_nuevos)
    assert libro_actualizado is None
    libros = gestor_datos2.cargar_datos(filepath)
    assert len(libros) == 2


def test_actualizar_libro_solo_un_campo(libros_con_datos):
    """Debe poder actualizar solo un campo."""
    filepath = libros_con_datos
    isbn_a_actualizar = '978-0743273565'
    datos_nuevos = {'stock': 7}
    libro_actualizado = actualizar_libro(filepath, isbn_a_actualizar, datos_nuevos)
    assert libro_actualizado is not None
    assert libro_actualizado['stock'] == '7'
    assert libro_actualizado['nombre'] == 'Cien años de soledad'
    assert libro_actualizado['autor'] == 'Gabriel García Márquez'


# --- Tests para eliminar_libro ---

def test_eliminar_libro_existente(libros_con_datos):
    """Debe eliminar un libro existente."""
    filepath = libros_con_datos
    isbn_a_eliminar = '978-0321765723'
    resultado = eliminar_libro(filepath, isbn_a_eliminar)
    assert resultado is True
    libros_actualizados = gestor_datos2.cargar_datos(filepath)
    assert len(libros_actualizados) == 1
    assert not any(libro['ISBN'] == isbn_a_eliminar for libro in libros_actualizados)


def test_eliminar_libro_no_existente(libros_con_datos):
    """No debe eliminar nada si el ISBN no existe."""
    filepath = libros_con_datos
    isbn_no_existente = '111-1111111111'
    resultado = eliminar_libro(filepath, isbn_no_existente)
    assert resultado is False
    libros_actualizados = gestor_datos2.cargar_datos(filepath)
    assert len(libros_actualizados) == 2


def test_eliminar_libro_lista_vacia(libros_vacios):
    """No debe eliminar nada si la lista está vacía."""
    filepath = libros_vacios
    isbn_a_eliminar = 'cualquier-isbn'
    resultado = eliminar_libro(filepath, isbn_a_eliminar)
    assert resultado is False
    libros_actualizados = gestor_datos2.cargar_datos(filepath)
    assert len(libros_actualizados) == 0
