from PyQt5.QtWidgets import QMessageBox
from dao.conexion import Conexion
import pyodbc
class UsuarioDAO:
    def __init__(self):
        # Inicializa la conexión a la base de datos
        self.conexion = Conexion()
        self.cursor = self.conexion.conn.cursor()  # Obtiene el cursor a través de la conexión
        
    def validar_usuario(self, username, password):
        """
        Valida el usuario y la contraseña.
        :param username: Nombre de usuario del jugador.
        :param password: Contraseña del jugador.
        :return: True si las credenciales son válidas, False en caso contrario.
        """
        try:
            # Verificar si el usuario ya existe y obtener la contraseña almacenada
            sql_check = '''SELECT clave FROM Usuarios WHERE username = ?'''
            self.cursor.execute(sql_check, (username,))
            result = self.cursor.fetchone()

            if result:
                stored_password = result[0]  # Obtener la contraseña almacenada
                if stored_password == password:
                    # Si el usuario ya existe y la contraseña es correcta, dar la bienvenida
                    QMessageBox.information(None, "Bienvenido", f"Bienvenido: {username}")
                    print(f"Bienvenido, {username}")
                    return True  # Usuario existente con la contraseña correcta
                else:
                    # Si la contraseña es incorrecta, mostrar mensaje de error
                    QMessageBox.warning(None, "Error de contraseña", f"La contraseña no coincide con la registrada.")
                    print(f"La contraseña no coincide con la registrada.")
                    return False  # Contraseña incorrecta
            else:
                # Si el usuario no existe, mostrar un mensaje
                QMessageBox.warning(None, "Usuario no encontrado", f"El usuario '{username}' no existe.")
                print(f"El usuario '{username}' no existe.")
                return False  # Usuario no encontrado

        except Exception as e:
            # Error encontrado
            QMessageBox.warning(None, "Error al validar usuario", f"Error: {e}")
            return False  # Validación fallida
        
    def mostrar_usuario_actual(self, username):
        """
        Devuelve el username del usuario que está jugando.
        :param username: Nombre de usuario del jugador actual.
        :return: Username del usuario actual.
        """
        return username if username else None
    
    def eliminar_usuario(self, idusuario):
        """
        FUNCIÓN AÚN SIN IMPLEMENTAR
        Elimina un usuario de la base de datos.
        :param idusuario: ID del usuario a eliminar.
        :return: True si la eliminación fue exitosa, False en caso contrario.
        """
        try:
            # Eliminar el usuario de la base de datos
            sql_delete = '''DELETE FROM Usuarios WHERE idusuario =?'''
            self.cursor.execute(sql_delete, (idusuario,))
            self.conexion.conn.commit()  # Confirmar la eliminación
            QMessageBox.information(None, "Eliminación exitosa", f"Usuario eliminado correctamente.")
            print(f"Usuario eliminado con éxito: {idusuario}")
            
        except Exception as e:
            # Captura cualquier otro error y muestra un mensaje de advertencia
            QMessageBox.warning(None, "Error al eliminar usuario", f"Error: {e}")
            print(f"Error al eliminar usuario: {e}")
            return False  # Eliminación fallida
            
    def insertar_usuario(self, username, clave):
        """
        Inserta un nuevo usuario en la base de datos si no existe previamente.
        Si el nombre de usuario ya existe, muestra un mensaje de advertencia.
        :param username: Nombre de usuario.
        :param clave: Contraseña del usuario.
        :return: True si la inserción fue exitosa, False en caso contrario.
        """
        try:
            # Verificar si el usuario ya existe
            sql_check = '''SELECT 1 FROM Usuarios WHERE username = ?'''
            self.cursor.execute(sql_check, (username,))
            if self.cursor.fetchone():
                # Si el usuario ya existe, mostrar un mensaje y no intentar insertar
                QMessageBox.warning(None, "Error de registro", f"El nombre de usuario '{username}' ya está en uso.")
                print(f"El usuario '{username}' ya existe.")
                return False  # El nombre de usuario ya está en uso
            
            # Intentar insertar el nuevo usuario
            sql_insert = '''INSERT INTO Usuarios (username, clave)
                            VALUES (?, ?)'''
            self.cursor.execute(sql_insert, (username, clave))
            self.conexion.conn.commit()  # Confirmar la inserción
            QMessageBox.information(None, "Registro exitoso", "Usuario insertado correctamente.")
            print(f"Registro exitoso del usuario {username}")
            return True  # Inserción exitosa

        except Exception as e:
            # Captura cualquier otro error y muestra un mensaje de advertencia
            QMessageBox.warning(None, "Error al insertar usuario", f"Error: {e}")
            print(f"Error al insertar usuario: {e}")
            return False  # Inserción fallida

        
    def obtener_id_usuario(self, username):
        """
        Obtiene el ID del usuario basado en el nombre de usuario.
        :param username: Nombre de usuario del jugador.
        :return: ID del usuario como entero si se encuentra, None en caso contrario.
        """
        sql = "SELECT idusuario FROM Usuarios WHERE username = ?;"
        try:
            self.cursor.execute(sql, (username,))
            result = self.cursor.fetchone()
            
            if result:
                user_id = int(result[0])
                print(f"ID del usuario '{username}': {user_id}")  # Imprimir el ID en consola
                return user_id
            else:
                print(f"Usuario '{username}' no encontrado.")  # Imprimir mensaje si no se encuentra
                return None
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al obtener ID de usuario: {e}")
            return None
        