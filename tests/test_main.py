import builtins
import main

# --- Test: elegir_almacenamiento() ---
def test_elegir_almacenamiento(monkeypatch):
    # Simula que el usuario elige "1"
    monkeypatch.setattr(builtins, "input", lambda _: "1")
    ruta = main.elegir_almacenamiento()
    assert "usuario.csv" in ruta

def test_elegir_almacenamiento_json(monkeypatch):
    # Simula que el usuario elige "2"
    monkeypatch.setattr(builtins, "input", lambda _: "2")
    ruta = main.elegir_almacenamiento()
    assert "usuario.json" in ruta


# --- Test: elegir_almacenamiento2() ---
def test_elegir_almacenamiento2(monkeypatch):
    # Simula que el usuario elige "1"
    monkeypatch.setattr(builtins, "input", lambda _: "1")
    ruta = main.elegir_almacenamiento2()
    assert "libro.csv" in ruta

def test_elegir_almacenamiento2_json(monkeypatch):
    # Simula que el usuario elige "2"
    monkeypatch.setattr(builtins, "input", lambda _: "2")
    ruta = main.elegir_almacenamiento2()
    assert "libro.json" in ruta


# --- Test: estructuras básicas ---
def test_constantes_definidas():
    assert main.DIRECTORIO_DATOS == "data"
    assert main.NOMBRE_ARCHIVO_JSON.endswith(".json")
    assert main.NOMBRE_ARCHIVO_CSV.endswith(".csv")