from PyQt5.QtWidgets import QOpenGLWidget, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QOpenGLTexture
from OpenGL.GL import *
import random
import pygame.mixer
import math

class OpenGLWidget(QOpenGLWidget):
    def __init__(self, game_window, pairs, timer_label, total_time_label, challenge=False):
        super().__init__(game_window)
        self.game_window = game_window
        self.pairs = pairs
        self.timer_label = timer_label
        self.total_time_label = total_time_label
        self.challenge = challenge
        
        self.max_clicks = 30

        self.card_positions = []
        self.card_colors = []
        self.flipped_cards = []
        self.flipping_cards = []
        self.selected_cards = []
        self.matched_cards = []
        self.back_texture = None
        self.click_count = 0  # Contador de clics
        
        self.flip_angles = [0] * (self.pairs * 2)  # Ángulos iniciales para animación

        # Configurar tiempo límite y temporizadores
        self.time_limit = 90 if self.challenge else 60
        self.remaining_time = self.time_limit
        self.total_time = 0

        self.configure_timers()
        
        # Inicializar sonidos
        pygame.mixer.init()  # Asegúrate de inicializar pygame mixer
        self.sound_correct = pygame.mixer.Sound("sounds/correct.mp3")  # Sonido de acierto
        self.sound_incorrect = pygame.mixer.Sound("sounds/wrong.mp3")  # Sonido de error
        
        # Generar cartas según el modo
        self.generate_cards() if not self.challenge else self.generate_master_challenge_cards()
        
    def configure_timers(self):
        """Configura los temporizadores necesarios para el widget."""
        # Temporizador para el tiempo restante
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_timer)
        self.time_timer.start(1000)

        # Temporizador para el tiempo total
        self.total_time_timer = QTimer(self)
        self.total_time_timer.timeout.connect(self.update_total_time)
        self.total_time_timer.start(1000)

        # Temporizador para checar cartas volteadas
        self.timer = QTimer(self)
        if self.challenge:
            self.timer.timeout.connect(self.check_flipped_cards_challenge)
        else:
            self.timer.timeout.connect(self.check_flipped_cards)

        # Temporizador para la animación de volteo
        if self.challenge:
            self.animation_timer = QTimer(self)
            self.animation_timer.timeout.connect(self.update_flip_challenge)
        else:
            self.animation_timer = QTimer(self)
            self.animation_timer.timeout.connect(self.update_flip_animation)
        
    def load_texture(self, file_path):
        print(f"Intentando cargar textura desde: {file_path}")
        image = QImage(file_path)
        if image.isNull():
            print(f"Error: No se pudo cargar la imagen desde {file_path}")
            return None  # Retorna None si la imagen no se carga
        else:
            print(f"Imagen cargada correctamente desde {file_path}")  # Mensaje de éxito

        texture = QOpenGLTexture(QOpenGLTexture.Target2D)
        texture.create()
        texture.setData(image)
        texture.setMinificationFilter(QOpenGLTexture.Linear)
        texture.setMagnificationFilter(QOpenGLTexture.Linear)
        print("Textura creada y configurada")
        return texture
    
    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.setText(f"Tiempo restante: {self.remaining_time}")
        else:
            self.time_timer.stop()
            if not self.challenge:
                self.game_over()
            else:
                self.challenge_over()
            
    def update_total_time(self):
        self.total_time += 1  # Incrementa el tiempo total cada segundo
        self.total_time_label.setText(f"Tiempo total: {self.total_time}s")
    
    def game_over(self):
        self.time_timer.stop()
        self.total_time_timer.stop()
        from dao.partida_dao import PartidaDAO
        partida = PartidaDAO()
        partida.insertar_partida(self.game_window.user_id, self.game_window.level, self.total_time, 0, self.game_window.click_count)
        print(f"Perdiste la partida en el nivel {self.game_window.level}")
        self.reset_game()
        QMessageBox.warning(self.game_window, "¡Tiempo Agotado!", "Se te ha acabado el tiempo. Reiniciando el nivel...")
        
    def challenge_over(self):
        self.time_timer.stop()
        self.total_time_timer.stop()
        from dao.partida_dao import PartidaDAO
        partida = PartidaDAO()
        partida.insertar_partida(self.game_window.user_id, self.game_window.level, self.total_time, 0, self.game_window.click_count)
        print(f"Perdiste el desafío en el nivel {self.game_window.level}")
        QMessageBox.warning(self.game_window, "¡Tiempo Agotado!", f"Se te ha acabado el tiempo. Llegasta hasta el desafío {self.game_window.level}. ¡Enhorabuena!")
        self.game_window.return_to_menu()

    
    def reset_game(self):
        self.time_timer.stop()
        self.total_time_timer.stop()  # Detener el temporizador total
        self.remaining_time = self.time_limit
        self.timer_label.setText(f"Tiempo restante: {self.remaining_time}")
        self.clear_card_states()
        self.generate_cards()
        self.hide_all_cards()
        self.time_timer.start(1000)  # Reinicia el temporizador
        self.total_time_timer.start(1000)  # Reinicia el temporizador total
        self.total_time = 0  # Reinicia el tiempo total
        self.total_time_label.setText(f"Tiempo total: {self.total_time} s")  # Reinicia la etiqueta
        self.show_all_cards_initially()
        self.click_count = 0
        self.game_window.click_label.setText(f"Clics: {self.click_count}")

    def clear_card_states(self):
        """Limpia el estado de las cartas y seleccionadas."""
        self.flipped_cards = [False] * (self.pairs * 2)
        self.selected_cards.clear()
        self.matched_cards.clear()
        self.card_colors.clear()  # Limpiar colores
        self.card_positions.clear()  # Limpiar posiciones

    def show_all_cards_initially(self):
        """Mostrar todas las cartas durante un segundo al inicio con un efecto de parpadeo"""
        self.flipped_cards = [True] * (self.pairs * 2)
        self.update()
        QTimer.singleShot(1200, self.hide_all_cards)

    def generate_cards(self):
        """Generar posiciones y colores de las cartas para 11 pares (22 cartas en total)"""
        available_colors = [
            (1, 0, 0),      # Rojo
            (0, 0, 1),      # Azul
            (1, 1, 0),      # Amarillo
            (0, 1, 0),      # Verde
            (0.5, 0, 0.5),  # Púrpura
            (1, 0.5, 0),    # Naranja
            (0, 1, 1),      # Cian
            (0.8, 0.4, 0),  # Marrón
            (0.8, 0.6, 0.8),# Lavanda
            (1, 0.75, 0.8), # Rosa
            (0.53, 0.81, 0.92),  # Celeste
            (1, 1, 1)       # Blanco
        ]

        selected_colors = random.sample(available_colors, self.pairs)  # Escoge los 10 colores
        self.card_colors = selected_colors * 2  # Duplicar para los pares
        random.shuffle(self.card_colors)  # Barajar los colores para aleatorizar su posición

        # Configurar la distribución de 5 columnas y 4 filas
        columns = 6
        card_width = 75  # Cartas más pequeñas
        card_height = 90  # Cartas más pequeñas
        x_spacing = 30  # Ajustar espacio horizontal entre cartas
        y_spacing = 30  # Ajustar espacio vertical entre cartas

        for i in range(self.pairs * 2):  # 22 cartas
            row, col = divmod(i, columns)
            x = 50 + col * (card_width + x_spacing)  # Posición X con espaciado
            y = 50 + row * (card_height + y_spacing)  # Posición Y con espaciado
            self.card_positions.append((x, y))
            self.flipped_cards.append(False)
            
        print("Estás jugando el modo normal")
            
    def generate_master_challenge_cards(self):
        """Generar posiciones y colores de las cartas en Desafío Maestro (escala de verdes con 12 tonos)"""
        # Colores en escala de verdes (12 tonos)
        available_colors = [
            (0, 1, 0),      # Verde puro
            (0, 0.8, 0),    # Verde oscuro
            (0, 0.5, 0),    # Verde bosque
            (0.3, 0.7, 0.3),# Verde claro
            (0.2, 0.8, 0.2),# Verde brillante
            (0.6, 1, 0.6),  # Verde pastel
            (0.4, 0.8, 0.4),# Verde intermedio
            (0, 1, 0.5),    # Verde lima
            (0.3, 0.9, 0.4),# Verde medio
            (0.5, 1, 0.7),  # Verde menta
            (0.8, 1, 0.8),  # Verde muy suave
            (1, 1, 1)       # Blanco
        ]

        # Seleccionar colores para los pares
        selected_colors = random.sample(available_colors, self.pairs)  # Escoge 12 tonos de verde
        self.card_colors = selected_colors * 2  # Duplicar para los pares
        random.shuffle(self.card_colors)  # Barajar los colores para aleatorizar su posición

        # Configurar la distribución de 6 columnas y 4 filas
        columns = 6
        card_width = 80  # Cartas más pequeñas
        card_height = 120  # Cartas más pequeñas
        x_spacing = 30  # Ajustar espacio horizontal entre cartas
        y_spacing = 30  # Ajustar espacio vertical entre cartas

        for i in range(self.pairs * 2):  # 24 cartas (12 pares)
            row, col = divmod(i, columns)
            x = 50 + col * (card_width + x_spacing)  # Posición X con espaciado
            y = 50 + row * (card_height + y_spacing)  # Posición Y con espaciado
            self.card_positions.append((x, y))
            self.flipped_cards.append(False)
            
        print("Estás jugando el modo difícil")

    def hide_all_cards(self):
        """Ocultar todas las cartas después de mostrarlas brevemente"""
        self.flipped_cards = [False] * (self.pairs * 2)
        self.update()

    def update_flip_animation(self):
        """Actualizar la animación de volteo"""
        updated = False
        for i in range(len(self.flip_angles)):
            if i in self.flipping_cards:
                if self.flipped_cards[i]:  # Si la carta está siendo volteada hacia adelante
                    if self.flip_angles[i] < 180:
                        self.flip_angles[i] += min(20, 180 - self.flip_angles[i])  # Suave
                        updated = True
                    else:
                        self.flipping_cards.remove(i)  # El giro ha terminado
                else:  # Si la carta está siendo volteada hacia atrás
                    if self.flip_angles[i] > 0:
                        self.flip_angles[i] -= min(20, self.flip_angles[i])  # Suave
                        updated = True
                    else:
                        self.flipping_cards.remove(i)  # El giro ha terminado

        if not updated:  # Si ya no hay animación en progreso
            self.flipping_cards.clear()
            self.animation_timer.stop()

        self.update()
        
    def update_flip_challenge(self):
        """Actualizar la animación de volteo con efecto de oscilación"""
        updated = False
        for i in range(len(self.flip_angles)):
            if i in self.flipping_cards:
                if self.flipped_cards[i]:  # Si la carta está siendo volteada hacia adelante
                    if self.flip_angles[i] < 360:
                        # Efecto de aceleración y desaceleración con seno (más suave)
                        oscillation_factor = math.sin(math.radians(self.flip_angles[i]))  # Oscilación
                        speed = min(20 + oscillation_factor * 10, 360 - self.flip_angles[i])  # Variar velocidad
                        self.flip_angles[i] += speed
                        updated = True
                    else:
                        self.flip_angles[i] = 360
                        self.flipping_cards.remove(i)  # El giro ha terminado
                else:  # Si la carta está siendo volteada hacia atrás
                    if self.flip_angles[i] > 0:
                        # Efecto de desaceleración con seno (más suave)
                        oscillation_factor = math.sin(math.radians(self.flip_angles[i]))  # Oscilación
                        speed = min(20 + oscillation_factor * 10, self.flip_angles[i])  # Variar velocidad
                        self.flip_angles[i] -= speed
                        updated = True
                    else:
                        self.flip_angles[i] = 0  # Asegurarse de que llegue a 0°
                        self.flipping_cards.remove(i)  # El giro ha terminado
            else:
                # Si la carta ya está completamente volteada, puedes agregar un pequeño rebote visual.
                if self.flip_angles[i] == 360:
                    self.flip_angles[i] = 359  # Rebote para simular "detenerse" ligeramente
                    updated = True

        if not updated:
            self.flipping_cards.clear()
            self.animation_timer.stop()

        self.update()
    def mousePressEvent(self, event):
        """Manejar clics para voltear cartas y contar clics"""
        self.game_window.click_count += 1  # Incrementa el contador de clics en GameWindow
        self.game_window.click_label.setText(f"Clics: {self.game_window.click_count}")  # Actualiza la etiqueta de clics
        
        x, y = event.x(), event.y()
        for i, pos in enumerate(self.card_positions):
            if pos[0] < x < pos[0] + 100 and pos[1] < y < pos[1] + 150:
                if not self.flipped_cards[i] and len(self.selected_cards) < 2:
                    self.flipping_cards.append(i)  # Añadir carta a la animación
                    self.flipped_cards[i] = True
                    self.selected_cards.append(i)
                    self.animation_timer.start(20)  # Cambiar el intervalo a 20 para una animación más suave
                    
                    if len(self.selected_cards) == 2:
                        self.timer.start(1000)

    def initializeGL(self):
        """Inicializar configuración de OpenGL"""
        glClearColor(0.2, 0.2, 0.2, 0.2)
        glEnable(GL_TEXTURE_2D)
        self.back_texture = self.load_texture("texturas/backside.jpg")
        if self.back_texture is None:
            print("Error cargando la textura del reverso de la carta")
        else:
            print("Textura del reverso de la carta cargada correctamente")

    def resizeGL(self, w, h):
        """Actualizar las dimensiones de la ventana OpenGL"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
    
    def paintGL(self):
        # Limpiar los buffers de color y profundidad
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Dibujar las cartas si la textura está creada
        if self.back_texture is not None:
            for i, pos in enumerate(self.card_positions):
                is_flipped = self.flipped_cards[i]
                color = self.card_colors[i] if is_flipped else (1, 0.7, 0.1)
                self.draw_card(pos[0], pos[1], color, self.flip_angles[i], is_flipped)
        else:
            print("Textura no creada.")

    def draw_card(self, x, y, color, angle, is_flipped):
        """Dibujar una carta como un prisma rectangular con rotación"""
        # Disminuir el tamaño de la carta
        thickness = 7.5  # Grosor de la carta (75% del original)
        width = 75  # Ancho de la carta (75% del original)
        height = 112.5  # Alto de la carta (75% del original)
        
        glPushMatrix()
        glTranslatef(x + width / 2, y + height / 2, 0)  # Trasladar para rotar en el centro
        glRotatef(angle, 0, 1, 0)  # Rotar en el eje Y
        glTranslatef(-width / 2, -height / 2, 0)  # Volver a su lugar original

        if is_flipped:
            # Dibujar el lado frontal
            glColor3f(*color)  # Color de la carta
            self.draw_quad(0, 0, width, height, color, offset=0)  # Frontal
        else:
            # Dibujar el reverso con textura
            if self.back_texture:
                glEnable(GL_TEXTURE_2D)
                self.back_texture.bind()
                glColor3f(1, 1, 1)  # Color blanco para no alterar la textura
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex3f(0, 0, 0)
                glTexCoord2f(1, 0); glVertex3f(width, 0, 0)
                glTexCoord2f(1, 1); glVertex3f(width, height, 0)
                glTexCoord2f(0, 1); glVertex3f(0, height, 0)
                glEnd()
                glDisable(GL_TEXTURE_2D)
            else:
                print("Error: La textura del reverso no está disponible")
                self.draw_quad(0, 0, width, height, (0.5, 0.5, 0.5), offset=0)  # Mostrar el reverso sin textura

        # Dibuja las caras del prisma (la carta con grosor)
        self.draw_quad(0, 0, width, height, (0.5, 0.5, 0.5), offset=-thickness)  # Posterior

        # Lados (derecho e izquierdo)
        self.draw_side(width, 0, height, thickness, color)  # Derecho
        self.draw_side(0, 0, height, thickness, color)  # Izquierdo

        # Parte superior e inferior
        self.draw_top_or_bottom(0, 0, width, thickness, color)  # Inferior
        self.draw_top_or_bottom(0, height, width, thickness, color)  # Superior

        glPopMatrix()

    def draw_quad(self, x, y, width, height, color, offset=3):
        """Dibujar un cuadrado (cara de la carta)"""
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex3f(x, y, offset)
        glVertex3f(x + width, y, offset)
        glVertex3f(x + width, y + height, offset)
        glVertex3f(x, y + height, offset)
        glEnd()

    def draw_side(self, x, y, height, thickness, color):
        """Dibujar un lado (izquierda/derecha) de la carta"""
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex3f(x, y, 0)
        glVertex3f(x, y, -thickness)
        glVertex3f(x, y + height, -thickness)
        glVertex3f(x, y + height, 0)
        glEnd()

    def draw_top_or_bottom(self, x, y, width, thickness, color):
        """Dibujar la parte superior o inferior de la carta"""
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex3f(x, y, 0)
        glVertex3f(x + width, y, 0)
        glVertex3f(x + width, y, -thickness)
        glVertex3f(x, y, -thickness)
        glEnd()

    def check_flipped_cards(self):
        """Verificar si las cartas volteadas coinciden"""
        if len(self.selected_cards) < 2:
            return

        card1, card2 = self.selected_cards
        if self.card_colors[card1] == self.card_colors[card2]:
            self.matched_cards.extend([card1, card2])
            self.sound_correct.play()  # Reproducir sonido de acierto
            if len(self.matched_cards) == len(self.card_positions):
                self.game_window.show_level_complete()
        else:
            self.sound_incorrect.play()  # Reproducir sonido de error
            self.flipping_cards.extend(self.selected_cards)  # Añadir a la animación para voltearlas de nuevo
            self.flipped_cards[card1] = False
            self.flipped_cards[card2] = False
            self.animation_timer.start(50)

        self.selected_cards.clear()
        self.timer.stop()
        self.update()

    def check_flipped_cards_challenge(self):
        """Verificar si las cartas volteadas coinciden (Para el desafío)"""
        if self.challenge:
            if len(self.selected_cards) < 2:
                return

            card1, card2 = self.selected_cards
            if self.card_colors[card1] == self.card_colors[card2]:
                self.matched_cards.extend([card1, card2])
                self.sound_correct.play()  # Reproducir sonido de acierto
                if len(self.matched_cards) == len(self.card_positions):
                    self.game_window.show_challenge_complete()
            else:
                self.sound_incorrect.play()  # Reproducir sonido de error
                # Añadir cartas a la animación para voltearlas de nuevo
                self.flipping_cards.extend(self.selected_cards)
                self.flipped_cards[card1] = False
                self.flipped_cards[card2] = False
                self.animation_timer.start(50)

            # Limpiar selección y detener temporizador
            self.selected_cards.clear()
            self.timer.stop()
            self.update()
