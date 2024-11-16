from dao.conexion import Conexion
from model.nivel import Nivel
from datetime import datetime
import pyodbc as sql

class NivelDAO:
    def __init__(self):
        self.conn = Conexion()
        self.cursor = self.conn.cursor()
        
    