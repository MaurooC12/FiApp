# models/conexion.py
import sqlitecloud

# Conexión a SQLite Cloud
def get_connection():
    conn = sqlitecloud.connect(
        "sqlitecloud://cqatl0c3hk.g4.sqlite.cloud:8860/fiador?apikey=pZyH4Qbz5XDD5EY68XZ8A5akaFZbQv4L2JrsGMDvZYQ"
    )
    conn.execute("USE DATABASE fiador")
    return conn
