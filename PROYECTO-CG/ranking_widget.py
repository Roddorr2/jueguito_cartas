from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem

class RankingWidget(QWidget):
    def __init__(self, top_10_data):
        super().__init__()
        self.setWindowTitle("Ranking de Jugadores")
        self.setGeometry(300, 300, 450, 350)
        self.setMinimumSize(450, 350)  # Tamaño mínimo de ventana
        
        # Crear layout
        layout = QVBoxLayout()

        # Crear la tabla
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)  # Número de columnas
        self.table_widget.setHorizontalHeaderLabels(["Username", "Descripción", "Tiempo", "Fecha de Partida"])
        
        # Ajustar el tamaño de la tabla
        self.table_widget.setRowCount(len(top_10_data))
        
        # Llenar la tabla con los datos de la lista
        for row, (username, descripcion, tiempo, fechapartida) in enumerate(top_10_data):
            self.table_widget.setItem(row, 0, QTableWidgetItem(username))
            self.table_widget.setItem(row, 1, QTableWidgetItem(descripcion))
            self.table_widget.setItem(row, 2, QTableWidgetItem(tiempo))
            self.table_widget.setItem(row, 3, QTableWidgetItem(fechapartida))

        # Agregar la tabla al layout
        layout.addWidget(self.table_widget)
        
        # Establecer el layout
        self.setLayout(layout)
