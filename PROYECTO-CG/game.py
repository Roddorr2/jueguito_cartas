from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QTimer
import pygame
from opengl_widget import OpenGLWidget
from menu import MenuWindow
from dao.partida_dao import PartidaDAO


class GameWindow(QMainWindow):
    def __init__(self, user_id, level, username=None):
        super().__init__()
        pygame.mixer.init() 
        self.user_id = user_id
        self.level = level
        self.pairs = level + 1
        self.username = username
        
        self.click_count = 0  # Contador de clics
        self.click_label = QLabel("Clics: 0", self)  # Etiqueta para mostrar el contador de clics
        self.click_label.move(10, 50)  # Ubicación en la ventana
        self.click_label.setStyleSheet("font-size: 16px; color: rgb(6, 107, 45)")  # Estilo opcional
        self.setWindowTitle(f"Nivel {level}")
        self.setGeometry(100, 100, 750, 800)
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Layout horizontal para las etiquetas
        self.timer_layout = QHBoxLayout()

        # Etiqueta para el tiempo restante
        self.timer_label = QLabel("Tiempo restante: 60s", self)
        self.timer_label.setStyleSheet("font-size: 16px; color: rgb(6, 107, 45)")
        self.timer_label.setFixedSize(150, 30)
        self.timer_layout.addWidget(self.timer_label)

        # Etiqueta para el tiempo total
        self.total_time_label = QLabel("Tiempo total: 0 s", self)
        self.total_time_label.setStyleSheet("font-size: 16px; color: rgb(6, 107, 45)")
        self.total_time_label.setFixedSize(150, 30)
        self.timer_layout.addWidget(self.total_time_label)

        # Añadir el layout de tiempo al layout principal
        self.layout.addLayout(self.timer_layout)

        # Widget OpenGL para las cartas
        self.opengl_widget = OpenGLWidget(self, self.pairs, self.timer_label, self.total_time_label)  # Pasar la etiqueta de tiempo total
        self.layout.addWidget(self.opengl_widget)

        # Mostrar todas las cartas brevemente al iniciar el nivel
        self.opengl_widget.show_all_cards_initially()
        
        pygame.mixer.music.load("sounds/bg_music.mp3")
        pygame.mixer.music.play(-1)  # Reproducir en bucle infinito

    def show_level_complete(self):
        """Mostrar mensaje y botón al completar un nivel"""
        self.opengl_widget.time_timer.stop()  # Detener el temporizador
        self.opengl_widget.total_time_timer.stop()  # Detener el conteo del tiempo

        # Detener la música de fondo
        pygame.mixer.music.stop()
        
        pygame.mixer.music.load("sounds/victory.mp3")  # Cargar la música de nivel completado
        pygame.mixer.music.play()  # Reproducir una vez
        
        # Crear el QLabel para el mensaje
        msg = QLabel("¡Nivel Completado!", self)
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
        mensaje.setText(f"Nivel {self.level} completado en {self.opengl_widget.total_time} segundos")
        mensaje.exec_()  # Muestra el cuadro de mensaje hasta que el usuario lo cierre
        print(f"Nivel {self.level} completado en {self.opengl_widget.total_time} segundos")

        # Agregar partida en la BD usando el `user_id` y `username` actuales
        print(f"Tipo de total_time: {type(self.opengl_widget.total_time)}, Valor: {self.opengl_widget.total_time}")
        partida = PartidaDAO()
        partida.insertar_partida(self.user_id, self.level, self.opengl_widget.total_time, 1)
        
        QTimer.singleShot(1500, self.show_next_or_return_button)  # Espera 1.5 segundo antes de mostrar el botón


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
            next_button.clicked.connect(self.go_to_next_level)
            self.layout.addWidget(next_button)
        else:
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
    
    def go_to_next_level(self):
        self.clear_game()
        if self.level < 11:  # Supongamos que hay 11 niveles
            from dao.usuario_dao import UsuarioDAO
            usuario_dao = UsuarioDAO()
            self.user_id = usuario_dao.obtener_id_usuario(self.username)
            self.close()
            next_window = GameWindow(self.user_id, self.level + 1, self.username)  # Mantener el user_id
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
        
    