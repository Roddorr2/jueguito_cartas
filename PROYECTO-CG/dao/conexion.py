import pyodbc

# Conexión a base de datos SQL Server
class Conexion:
    def __init__(self):
        try:
            self.conn = pyodbc.connect(
                'DRIVER={ODBC Driver 18 for SQL Server};'
                'SERVER=DESKTOP-FD6F8F2;'
                'DATABASE=juego_memoria;'
                'UID=sa;'
                'PWD=123456789;'
                'TrustServerCertificate=yes;'
            )
            self.cursor = self.conn.cursor()
            print('Conexión exitosa a SQL Server')
        except Exception as e:
            print(f"Error encontrado en {e}")
            self.conn = None
    
    