# -*- coding: utf-8 -*-
"""
Módulo de Préstamos
-------------------
Se encarga de registrar los préstamos de productos (libros) a clientes.
Guarda los datos en un archivo JSON.
"""


from datetime import date
import gestor_datos
import gestor_datos3
import usuario
import libro

def realizar_prestamo(archivo_prestamo:str,archivo_cliente:str,archivo_producto:str,id_cliente:str,id_producto:str):

    """
    Registra un préstamo nuevo  si el usuario y el producto existen
    Args:
        archivo_prestamo (str): Ruta del archivo JSON de préstamos.
        archivo_cliente (str): Ruta del archivo CSV de clientes.
        archivo_producto (str): Ruta del archivo CSV de producto.
        id_cliente (str): ID del cliente que solicita el préstamo.
        id_producto (str): ID del producto que se prestará.

    Returns:
        dict | None: El préstamo registrado o None si hubo error.
    """


    prestamos=gestor_datos.cargar_datos(archivo_prestamo)
    producto=gestor_datos.cargar_datos(archivo_producto)

    usuario=cliente.buscar_cliente_por_documento(archivo_cliente,id_cliente)
    if not usuario:
        print("❌ El usuario no existe")
        return  None

    prod=producto.buscar_cliente_por_producto(archivo_producto,id_producto)
    if not prod:
        print("❌ El producto no existe")
        return None

    if int(prod.get('stock',0))<=0:
        print("❌ No hay stock disponible para este producto")
        return None

    id_prestamo=len(prestamos)+1
    nuevo_prestamo={
        "id_prestamo": id_prestamo,
        "id_cliente": id_cliente,
        "id_producto": id_producto,
        "fecha_prestamo":str(date.today()),
        "estado":"prestado"
    }

    prestamos.append(nuevo_prestamo)

    prod['stock']=str(int(prod['stock'])-1)
    gestor_datos.guardar_datos(archivo_producto,producto)

    gestor_datos.guardar_datos(archivo_prestamo,prestamos)
    print("✅ Prestamo registrado con éxito")
    return nuevo_prestamo

def registrar_devolucion(archivo_prestamo: str, archivo_productos: str, id_prestamo: str):
    """
    Registra la devolución de un producto prestado, cambiando su estado y aumentando el stock.

    Args:
        archivo_prestamo (str): Ruta del archivo JSON de préstamos.
        archivo_productos (str): Ruta del archivo CSV de productos.
        id_prestamo (str): ID del préstamo que se desea devolver.

    Returns:
        dict | None: El préstamo actualizado o None si no se encuentra.
    """

    prestamos=gestor_datos.cargar_datos(archivo_prestamo)
    archivo_productos=gestor_datos.cargar_datos(archivo_productos)

    prestamo=next((p for p in prestamos if p.get('id_prestamo')==str(id_prestamo)),None)
    if not prestamo:
        print("❌ No se encontro el prestamo indicado")
        return None

    if prestamo.get("estado")=="devuelto":
        print("⚠️ El préstamo ya fue devuelto")
        return None

    prestamo['estado']="devuelto"

    producto_id=prestamo['id_producto']
    prod=next((p for p in archivo_productos if p.get("id")==producto_id),None)

    if prod:
        prod['stock']=str(int(prod['stock'])+1)

    gestor_datos.guardar_datos(archivo_prestamo,prestamos)
    gestor_datos3.guardar_datos(archivo_productos,producto)

    print("✅ Devolución registrada correctamente")
    return prestamo




