from datetime import datetime, timedelta
from dao.conexion import Conexion

class PartidaDAO:
    def __init__(self):
        self.conn = Conexion()
        self.cursor = self.conn.conn.cursor()
    
    from datetime import datetime, timedelta

class PartidaDAO:
    def __init__(self):
        self.conn = Conexion()
        self.cursor = self.conn.conn.cursor()
    
    def insertar_partida(self, idusuario, idnivel, tiempo, resultado):
        try:
            # Capturamos la fecha actual
            fechapartida = datetime.now().date()  # Solo la fecha actual
            
            # Convertir el tiempo a tipo TIME
            if isinstance(tiempo, int):  # Si tiempo es un entero (segundos)
                tiempo_str = str(timedelta(seconds=tiempo))  # Convertir a formato HH:MM:SS
            else:
                tiempo_str = tiempo  # Asumir que ya es un string en formato HH:MM:SS
            
            tiempo_partida = datetime.strptime(tiempo_str, '%H:%M:%S').time()  # Convertir a objeto TIME
            
            print(f"Tipos de parámetros: {type(idusuario)}, {type(idnivel)}, {type(tiempo_partida)}, {type(fechapartida)}, {type(resultado)}")
            
            # Consulta de inserción
            query = """INSERT INTO Partidas (idusuario, idnivel, tiempo, fechapartida, resultado) 
                    VALUES (?, ?, ?, ?, ?)"""
            
            # Ejecutar la consulta
            self.cursor.execute(query, (idusuario, idnivel, tiempo_partida, fechapartida, resultado))
            self.conn.conn.commit()
            
            # Mensaje en consola si la partida se inserta correctamente
            print("¡Partida ingresada correctamente!")
            print(f" - ID Usuario: {idusuario}\n"
                  f" - ID Nivel: {idnivel}\n"
                  f" - Tiempo: {tiempo_partida}\n"
                  f" - Fecha de Partida: {fechapartida}\n"
                  f" - Resultado: {resultado}")
            
        except Exception as e:
            # Imprimir error en consola si ocurre alguna excepción
            print(f"Error al insertar partida en la base de datos: {e}")
            
    def mostrar_partidas(self, idusuario):
        """
        Obtiene todas las partidas de un usuario específico y las devuelve en una lista.
        :param idusuario: ID del usuario.
        :return: Lista de partidas del usuario.
        """
        query = """
            SELECT tiempo,
                fechapartida,
                IIF(resultado = 1, 'GANADA', 'PERDIDA') AS resultado
            FROM Partidas
            WHERE idusuario = ?
        """
        
        partidas = []
        with self.conn.conn.cursor() as cursor:
            cursor.execute(query, (idusuario,))
            partidas = cursor.fetchall()
            
        # Formatear datos si es necesario (e.g., convertir fechas, tiempo a formato adecuado)
        formatted_partidas = [(partida[0], partida[1].strftime('%Y-%m-%d'), partida[2]) for partida in partidas]
        
        return formatted_partidas

            
    def ver_top_ten(self):
        """
        Obtiene los 10 usuarios con más puntaje en partidas ganadas y los devuelve en una lista.
        :return: lista de tuplas con el nombre de usuario y sus detalles.
        """
        
        sql = """
            SELECT TOP 10
                U.username,
                N.descripcion,
                P.tiempo,
                P.fechapartida
            FROM Partidas P
            INNER JOIN Usuarios U ON P.idusuario = U.idusuario
            INNER JOIN Niveles N ON P.idnivel = N.idnivel
            WHERE P.resultado = 1
            ORDER BY P.tiempo ASC
        """
        
        try:
            self.cursor.execute(sql)
            resultados = self.cursor.fetchall()

            # Crear una lista para almacenar los resultados
            top_ten = []
            for row in resultados:
                username = row[0]  # Username es el primer elemento
                descripcion = row[1]  # Descripción es el segundo elemento
                tiempo = str(row[2])  # Tiempo es el tercer elemento
                fechapartida = row[3].strftime('%Y-%m-%d')  # Fecha es el cuarto elemento

                top_ten.append((username, descripcion, tiempo, fechapartida))

            return top_ten
        
        except Exception as e:
            print(f"Error al obtener el top de usuarios: {e}")
            return []
