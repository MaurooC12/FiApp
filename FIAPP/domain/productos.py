# models/productos.py
from .conexion import get_connection

def crear_tabla():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT,
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def listar():
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM productos")
    datos = cursor.fetchall()
    conn.close()
    return datos

def agregar(nombre, categoria, precio, stock):
    conn = get_connection()
    conn.execute(
        "INSERT INTO productos (nombre, categoria, precio, stock) VALUES (?, ?, ?, ?)",
        (nombre, categoria, precio, stock),
    )
    conn.commit()
    conn.close()

def eliminar(id):
    conn = get_connection()
    conn.execute("DELETE FROM productos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
