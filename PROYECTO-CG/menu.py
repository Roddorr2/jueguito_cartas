from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt
from dao.usuario_dao import UsuarioDAO

class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.original_button_style = """
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
        """
        self.initUI()
        

    def initUI(self):
        """Configurar la interfaz del menú principal"""
        self.setWindowTitle("Menú Principal")
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()

        # Título
        title = QLabel("Juego de Memorizar Cartas 3D", self)
        title.setStyleSheet("font-size: 25px; color: rgb(6, 107, 45)")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Ingreso de usuario
        user_label = QLabel("Ingresa tu usuario:", self)
        user_label.setStyleSheet("font-size: 15px; color: rgb(6, 107, 45)")
        layout.addWidget(user_label)

        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Nombre de usuario")
        self.user_input.textChanged.connect(self.check_inputs)
        layout.addWidget(self.user_input)

        # Ingreso de contraseña
        password_label = QLabel("Ingresa tu contraseña:", self)
        password_label.setStyleSheet("font-size: 15px; color: rgb(6, 107, 45)")
        layout.addWidget(password_label)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)  # Mostrar como contraseña
        self.password_input.textChanged.connect(self.check_inputs)
        layout.addWidget(self.password_input)

        # Inicializar botones del menú
        self.start_button = self.create_button("Jugar (Nivel 1)", self.start_game)
        self.profile_button = self.create_button("Crear perfil", self.create_profile)
        self.matches_button = self.create_button("Ver partidas", self.show_matches)
        self.top_10_button = self.create_button("Ranking", self.show_top_10)
        self.rules_button = self.create_button("Ver Reglas", self.show_rules)
        self.exit_button = self.create_button("Salir", self.close_btn)

        # Añadir botones al layout
        layout.addWidget(self.start_button)
        layout.addWidget(self.profile_button)
        layout.addWidget(self.matches_button)
        layout.addWidget(self.top_10_button)
        layout.addWidget(self.rules_button)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

        self.disable_buttons()  # Deshabilitar botones al inicio

    def create_button(self, text, handler):
        """Crear un botón con diseño mejorado y su respectivo manejador"""
        button = QPushButton(text, self)
        button.setStyleSheet(self.original_button_style)
        button.clicked.connect(handler)
        return button
    
    def check_inputs(self):
        """Habilitar botones solo si hay un usuario y contraseña ingresados"""
        user_filled = bool(self.user_input.text().strip())
        password_filled = bool(self.password_input.text().strip())
        
        if user_filled and password_filled:
            self.start_button.setEnabled(True)
            self.profile_button.setEnabled(True)
            self.matches_button.setEnabled(True)
            self.top_10_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
            self.profile_button.setEnabled(False)
            self.matches_button.setEnabled(False)
            self.top_10_button.setEnabled(False)

    def create_profile(self):
        """Crear un nuevo usuario en el menú"""
        username = self.user_input.text().strip()
        password = self.password_input.text().strip()
        
        # Crear una instancia de UsuarioDAO
        usuario_dao = UsuarioDAO()
        
        # Intentar insertar el usuario en la base de datos
        if usuario_dao.insertar_usuario(username, password):
            # Usuario insertado correctamente, obtener el ID del usuario
            user_id = usuario_dao.obtener_id_usuario(username)  # Obtener ID del usuario usando el username
            
            # Ahora pasamos ambos username y user_id a GameWindow
            from game import GameWindow
            self.game_window = GameWindow(user_id=user_id, level=1, username=username)  # Pasar username también
            self.game_window.show()
            self.close()    

    def start_game(self):
        """Iniciar el juego en un nivel específico"""
        username = self.user_input.text().strip()
        password = self.password_input.text().strip()

        # Crear una instancia de UsuarioDAO
        usuario_dao = UsuarioDAO()
        
        # Validar usuario
        if usuario_dao.validar_usuario(username, password):         
            
            # Si la validación es exitosa, obtener el ID del usuario e iniciar el juego
            from game import GameWindow
            user_id = usuario_dao.obtener_id_usuario(username)
            
            # Pasar username y user_id a GameWindow
            self.game_window = GameWindow(user_id=user_id, level=1, username=username)
            self.game_window.show()
            self.close()

    def show_matches(self):
        """Mostrar la ventana de selección de partidas"""
        username = self.user_input.text().strip()
        password = self.password_input.text().strip()

        # Crear una instancia de UsuarioDAO
        usuario_dao = UsuarioDAO()
        
        # Validar usuario
        if usuario_dao.validar_usuario(username, password):
            from dao.partida_dao import PartidaDAO

            partida_dao = PartidaDAO()

            # Obtener el ID del usuario
            user_id = usuario_dao.obtener_id_usuario(username)
            
            # Obtener las partidas del usuario
            partidas = partida_dao.mostrar_partidas(user_id)
            
            # Verificar si se obtuvieron partidas
            print("Datos de partidas:", partidas) 
            
            # Mostrar diálogo de partidas
            from partida_dialog import PartidasDialog
            dialog = PartidasDialog(partidas, self)  # Crea el diálogo modal
            dialog.exec_()  # Muestra el diálogo y bloquea la interacción con la ventana principal
        else:
            QMessageBox.warning(self, "Error de Autenticación", "Usuario o contraseña incorrectos.")

    

    def show_top_10(self):
        """Mostrar el top 10 de jugadores con mejores puntajes"""
        from dao.partida_dao import PartidaDAO

        partida_dao = PartidaDAO()

        # Obtener el top 10 de usuarios
        top_10 = partida_dao.ver_top_ten()
        
        # Verificar si se obtuvo algún resultado
        if top_10:  # top_10 es una lista de tuplas
            # Mostrar diálogo con el top 10 de jugadores
            from ranking_dialog import RankingDialog  # Asegúrate de importar el diálogo correcto
            dialog = RankingDialog(top_10, self)  # Pasa directamente la lista de tuplas
            dialog.exec_()  # Muestra el diálogo y bloquea la interacción con la ventana principal
        else:
            QMessageBox.information(self, "Sin Resultados", "No se encontraron jugadores en el top 10.")

        
    def close_btn(self):
        """Cierra la ventana del menú"""
        self.close()
    
    def disable_buttons(self):
        """Deshabilitar los botones del menú"""
        for button in [self.start_button, self.profile_button, self.matches_button, self.top_10_button]:
            button.setEnabled(False)
    
    def dim_buttons(self):
        """Oscurecer los botones de la ventana del menú"""
        for i in range(1, 7):  
            button = self.layout().itemAt(i).widget()
            button.setStyleSheet(""" 
                QPushButton {
                    background-color: #2E7D32;  /* Color más oscuro */
                    color: white;
                    border-radius: 10px;
                    font-size: 16px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #2A6A28;
                }
            """)
            
    def closeEvent(self, event):
        """Cierra el widget de partidas cuando se cierra el menú principal."""
        if hasattr(self, 'partidas_widget') and self.partida_widget.isVisible() and hasattr(self, 'ranking_widget') and self.ranking_widget.isVisible():
            self.partidas_widget.close()  # Cerrar PartidasWidget si está abierto
            self.ranking_widget.close()  # Cerrar RankingWidget si está abierto
        super().closeEvent(event)
            
    def reset_buttons(self):
        """Restaurar el estilo original de los botones"""
        for i in range(1, 7):
            button = self.layout().itemAt(i).widget()
            button.setStyleSheet(self.original_button_style)
            
    def enable_buttons(self):
        """Habilitar los botones de la ventana del menú"""
        # Solo habilitar botones específicos
        self.start_button.setEnabled(True)
        self.profile_button.setEnabled(True)
        self.matches_button.setEnabled(True)
        self.top_10_button.setEnabled(True)
        
        # Verifica si la ventana de partidas está cerrada y habilita el resto
        if not hasattr(self, 'partida_widget') or not self.partida_widget.isVisible():
            self.matches_button.setEnabled(True)
            self.top_10_button.setEnabled(True)

    def show_rules(self):
        """Mostrar las reglas del juego"""
        QMessageBox.information(self, "Reglas", 
                                "1. Ingrese un usuario y contraseña para comenzar el juego. (REGISTRADO)\n"
                                "2. Encuentra todas las parejas de cartas antes que se acabe el tiempo.")
