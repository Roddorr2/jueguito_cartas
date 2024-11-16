from PyQt5.QtWidgets import QVBoxLayout, QDialog
from partidas_widget import PartidasWidget

class PartidasDialog(QDialog):
    def __init__(self, partidas_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de Partidas")
        self.setGeometry(200, 200, 350, 250)
        self.setMinimumSize(350, 250)  # Tamaño mínimo de ventana

        layout = QVBoxLayout()

        # Crear instancia de PartidasWidget
        self.partidas_widget = PartidasWidget(partidas_data)
        layout.addWidget(self.partidas_widget)

        self.setLayout(layout)
