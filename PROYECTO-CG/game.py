from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QTimer
import pygame
from opengl_widget import OpenGLWidget
from menu import MenuWindow
from dao.partida_dao import PartidaDAO
from prediccion import Prediccion

class GameWindow(QMainWindow):
    def __init__(self, user_id, level, username=None, master_mode=False):
        super().__init__()
        pygame.mixer.init()
        self.user_id = user_id
        self.level = level
        self.pairs = level + 1
        self.username = username
        self.master_mode = master_mode
        
        if self.master_mode:
            self.time_limit = 90
        else:
            self.time_limit = 60
        
        self.click_count = 0  # Contador de clics
        self.click_label = QLabel("Clics: 0", self)  # Etiqueta para mostrar el contador de clics
        self.click_label.move(10, 50)  # Ubicación en la ventana
        self.click_label.setStyleSheet("font-size: 16px; color: rgb(6, 107, 45)")  # Estilo opcional
        self.setWindowTitle(f"Nivel {level}")
        self.setGeometry(50, 50, 750, 680)
        self.setMaximumSize(750, 680)
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Layout horizontal para las etiquetas
        self.timer_layout = QHBoxLayout()

        # Etiqueta para el tiempo restante
        if self.master_mode:
            self.timer_label = QLabel("Tiempo restante: 90s", self)
            self.timer_label.setStyleSheet("font-size: 16px; color: rgb(6, 107, 45)")
            self.timer_label.setFixedSize(150, 30)
            self.timer_layout.addWidget(self.timer_label)
        else:
            self.timer_label = QLabel("Tiempo restante: 60s", self)
            self.timer_label.setStyleSheet("font-size: 16px; color: rgb(6, 107, 45)")
            self.timer_label.setFixedSize(150, 30)
            self.timer_layout.addWidget(self.timer_label) 
            
        # Etiqueta para el tiempo total
        self.total_time_label = QLabel("Tiempo total: 0s", self)
        self.total_time_label.setStyleSheet("font-size: 16px; color: rgb(6, 107, 45)")
        self.total_time_label.setFixedSize(150, 30)
        self.timer_layout.addWidget(self.total_time_label)

        # Añadir el layout de tiempo al layout principal
        self.layout.addLayout(self.timer_layout)

        # Widget OpenGL para las cartas
        if self.master_mode:
            self.opengl_widget = OpenGLWidget(self, self.pairs, self.timer_label, self.total_time_label, challenge=True)
        else: 
            self.opengl_widget = OpenGLWidget(self, self.pairs, self.timer_label, self.total_time_label, challenge=False)
            
        self.layout.addWidget(self.opengl_widget)

        # Mostrar todas las cartas brevemente al iniciar el nivel
        self.opengl_widget.show_all_cards_initially()
        if self.master_mode:
            pygame.mixer.music.load("sounds/challenge_bg_music.mp3")
        else:
            pygame.mixer.music.load("sounds/bg_music.mp3")
            
        pygame.mixer.music.play(-1)  # Reproducir en bucle infinito
        
        # Botón para guardar partida durante el juego
        if not self.master_mode:
            self.save_button = QPushButton("Guardar Partida", self)
            self.save_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 10px;
                    font-size: 16px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            self.save_button.clicked.connect(self.save_match)  # Conectar el botón con el método save_match
            self.layout.addWidget(self.save_button)
        
    def show_challenge_complete(self):
        """Mostrar mensaje y botón al completar un desafío"""
        self.opengl_widget.time_timer.stop()  # Detener el temporizador
        self.opengl_widget.total_time_timer.stop()  # Detener el conteo del tiempo

        # Detener la música de fondo
        pygame.mixer.music.stop()
        
        pygame.mixer.music.load("sounds/victory.mp3")  # Cargar la música de nivel completado
        pygame.mixer.music.play()  # Reproducir una vez
        
        # Crear el QLabel para el mensaje
        msg = QLabel("¡Excelente!", self)
        msg.setStyleSheet("font-size: 24px; font-weight: bold; color: rgb(6, 107, 45);")
        msg.setAlignment(Qt.AlignCenter)

        # Crear un layout para centrar el mensaje
        message_layout = QVBoxLayout()
        message_layout.addStretch()  # Espaciador superior
        message_layout.addWidget(msg)
        message_layout.addStretch()  # Espaciador inferior

        # Agregar el layout del mensaje al layout principal
        self.layout.addLayout(message_layout)

        
        # Imprimir en consola el tiempo en el que se completó el nivel
        mensaje = QMessageBox()
        mensaje.setWindowTitle("Felicidades")
        mensaje.setText(f"Desafío {self.level} completado en {self.opengl_widget.total_time} segundos")
        mensaje.exec_()  # Muestra el cuadro de mensaje hasta que el usuario lo cierre
        print(f"Desafío {self.level} completado en {self.opengl_widget.total_time} segundos")

        # Agregar partida en la BD usando el `user_id` y `username` actuales
        print(f"Tipo de total_time: {type(self.opengl_widget.total_time)}, Valor: {self.opengl_widget.total_time}")
        partida = PartidaDAO()
        partida.insertar_partida(self.user_id, self.level, self.opengl_widget.total_time, 1, self.click_count)
        
        QTimer.singleShot(1500, self.show_next_or_return_button)  # Espera 1.5 segundo antes de mostrar el botón
        

    def show_level_complete(self):
        """Mostrar mensaje y botón al completar un nivel"""
        self.opengl_widget.time_timer.stop()  # Detener el temporizador
        self.opengl_widget.total_time_timer.stop()  # Detener el conteo del tiempo

        # Detener la música de fondo
        pygame.mixer.music.stop()
        pygame.mixer.music.load("sounds/victory.mp3")  # Cargar la música de nivel completado
        pygame.mixer.music.play()  # Reproducir una vez

        # Generar el mensaje personalizado según los clics
        personalized_message = self.get_personalized_message(self.level, self.click_count)

        # Crear el QLabel para el mensaje
        msg = QLabel(personalized_message, self)
        msg.setStyleSheet("font-size: 24px; font-weight: bold; color: rgb(6, 107, 45);")
        msg.setAlignment(Qt.AlignCenter)

        # Crear un layout para centrar el mensaje
        message_layout = QVBoxLayout()
        message_layout.addStretch()  # Espaciador superior
        message_layout.addWidget(msg)
        message_layout.addStretch()  # Espaciador inferior

        # Agregar el layout del mensaje al layout principal
        self.layout.addLayout(message_layout)
        
        # self.save_button.setEnabled(False)  # Desactivar el botón de guardar
        self.save_button.setVisible(False)

        # Imprimir en consola el tiempo en el que se completó el nivel
        # mensaje = QMessageBox()
        # mensaje.setWindowTitle("Felicidades")
        # mensaje.setText(f"Nivel {self.level} completado en {self.opengl_widget.total_time} segundos")
        # mensaje.exec_()  # Muestra el cuadro de mensaje hasta que el usuario lo cierre
        print(f"Nivel {self.level} completado en {self.opengl_widget.total_time} segundos")

        # Agregar partida en la BD usando el `user_id` y `username` actuales
        print(f"Tipo de total_time: {type(self.opengl_widget.total_time)}, Valor: {self.opengl_widget.total_time}")
        partida = PartidaDAO()
        partida.insertar_partida(self.user_id, self.level, self.opengl_widget.total_time, 1, self.click_count)
        
        QTimer.singleShot(1500, self.show_next_or_return_button)  # Espera 1.5 segundo antes de mostrar el botón

    def get_personalized_message(self, level, click_count):
        """Generar un mensaje personalizado basado en el nivel y los clics."""
        # Definir los clics ideales para cada nivel
        ideal_clicks = {
            1: 4,
            2: 6,
            3: 8,
            4: 10,
            5: 15,
            6: 20,
            7: 25,
            8: 30,
            9: 35,
            10: 40,
            11: 45
        }

        # Obtener el número ideal de clics para este nivel
        clicks_ideales = ideal_clicks.get(level, None)
        if clicks_ideales is None:
            return f"¡Nivel {level} completado! Buen trabajo."

        # Categorizar el desempeño
        if click_count == clicks_ideales:
            return f"¡Excelente! Completaste el nivel {level} a la primera."
        elif click_count < clicks_ideales + 5:  
            return f"¡Buen trabajo! Nivel {level} completado en {click_count} clics."
        else:
            return f"Podemos mejorar: completaste el nivel {level} en {click_count} clics. Sigue practicando."

    def show_next_or_return_button(self):
        """Mostrar botón para ir al siguiente nivel o volver al menú principal si es el último nivel"""
        if self.level < 11:  # Suponiendo que hay 11 niveles
            next_button = QPushButton("Siguiente Nivel", self)
            next_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 10px;
                    font-size: 16px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            if self.opengl_widget.challenge:
                next_button.clicked.connect(self.go_to_next_challenge)
            else:
                next_button.clicked.connect(self.go_to_next_level)

            # Agregar el botón al layout con un espaciador arriba para moverlo hacia arriba
            self.layout.addWidget(next_button)
            
        else:
            # Botón para volver al menú
            back_button = QPushButton("Volver al Menú", self)
            back_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 10px;
                    font-size: 16px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            back_button.clicked.connect(self.return_to_menu)
            self.layout.addWidget(back_button)

            # Botón para guardar datos
            save_button = QPushButton("Guardar Datos", self)
            save_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 10px;
                    font-size: 16px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            save_button.clicked.connect(self.save_data)  # Asegúrate de tener la función save_data definida
            self.layout.addWidget(save_button)
            
    def clear_game(self):
        """Limpiar el layout antes de iniciar el siguiente nivel"""
        self.click_count = 0
        self.click_label.setText(f"Clics: {self.click_count}")
        
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not self.opengl_widget:  # No eliminar el widget OpenGL
                if widget is not None:
                    widget.deleteLater()

        # Solo eliminar el widget OpenGL si ya no lo necesitas y piensas recrearlo
        if self.opengl_widget is not None:
            self.opengl_widget.deleteLater()
            self.opengl_widget = None  # Asegurarse de que no se acceda más al widget eliminado
            
    def save_match(self):
        from dao.usuario_dao import UsuarioDAO
        usuario_dao = UsuarioDAO()
        partida_dao = PartidaDAO()
        
        # Obtener el ID de usuario
        self.user_id = usuario_dao.obtener_id_usuario(self.username)
        
        # Guardar la partida
        partida_dao.insertar_partida(self.user_id, self.level-1, self.opengl_widget.total_time, 0, self.click_count)
        
        # Mostrar mensaje de éxito
        QMessageBox.information(None, "Partida guardada", "Partida guardada con éxito.")
    
    def save_data(self):
        partida_dao = PartidaDAO()
        from dao.usuario_dao import UsuarioDAO
        usuario_dao = UsuarioDAO()
        
        # Obtener el ID de usuario
        self.user_id = usuario_dao.obtener_id_usuario(self.username)
        
        # Abrir el explorador de archivos para elegir el directorio
        directory = QFileDialog.getExistingDirectory(None, "Seleccionar directorio", "")
        
        if directory:
            # Construir el nombre del archivo CSV
            file_name = f"{directory}/mejores_partidas_{self.username}.csv"
            
            # Exportar los datos a CSV
            partida_dao.exportar_datos_a_csv(self.user_id, file_name)
            
            # Instanciar la clase Prediccion y entrenar el modelo
            prediccion = Prediccion(file_name)
            prediccion.entrenar_y_predecir()

        else:
            print("El usuario no seleccionó un directorio.")
    def go_to_next_level(self):
        self.clear_game()
        if self.level < 11:  # Supongamos que hay 11 niveles
            from dao.usuario_dao import UsuarioDAO
            usuario_dao = UsuarioDAO()
            self.user_id = usuario_dao.obtener_id_usuario(self.username)
            self.close()
            next_window = GameWindow(self.user_id, self.level + 1, self.username, False)  # Mantener el user_id
            next_window.show()
        else:
            self.return_to_menu()   
            
    def go_to_next_challenge(self):
        self.clear_game()
        if self.level < 11:  # Supongamos que hay 11 niveles
            from dao.usuario_dao import UsuarioDAO
            usuario_dao = UsuarioDAO()
            self.user_id = usuario_dao.obtener_id_usuario(self.username)
            self.close()
            next_window = GameWindow(self.user_id, self.level + 1, self.username, True)  # Mantener el user_id
            next_window.show()
        else:
            self.return_to_menu()  

    def return_to_menu(self):
        """Volver al menú principal cuando se completa el último nivel"""
        self.opengl_widget.time_timer.stop()  # Detener el temporizador
        self.opengl_widget.total_time_timer.stop()  # Detener el conteo del tiempo

        # Detener la música de fondo
        pygame.mixer.music.stop()
        self.close()
        self.menu_window = MenuWindow()
        self.menu_window.show()
