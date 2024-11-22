from PyQt5.QtWidgets import QDialog, QVBoxLayout
from ranking_widget import RankingWidget  # Asegúrate de que la ruta sea correcta

class RankingDialog(QDialog):
    def __init__(self, top_10_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ranking de jugadores")
        self.setGeometry(300, 300, 600, 400)
        self.setMaximumSize(600, 400)
        
        # Crear un layout vertical
        layout = QVBoxLayout()

        # Crear el widget de ranking
        self.ranking_widget = RankingWidget(top_10_data)
        
        # Añadir widgets al layout
        layout.addWidget(self.ranking_widget)
        
        self.setLayout(layout)
