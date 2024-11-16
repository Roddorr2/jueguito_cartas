from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QDialog

class PartidasWidget(QWidget):
    def __init__(self, partidas_data):
        super().__init__()
        self.setWindowTitle("Historial de Partidas")
        self.setGeometry(200, 200, 350, 250)
        self.setMinimumSize(350, 250)  # Tamaño mínimo de ventana
        
        layout = QVBoxLayout()
        
        # Etiqueta de título
        label = QLabel("Partidas registradas en este perfil")
        layout.addWidget(label)
        
        # Tabla para mostrar partidas
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Número de columnas según los datos
        self.table.setHorizontalHeaderLabels(["Tiempo", "Fecha", "Resultado"])
        
        # Rellenar la tabla con datos de partidas
        self.table.setRowCount(len(partidas_data))
        for row, partida in enumerate(partidas_data):
            for col, value in enumerate(partida):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
        
        self.table.resizeColumnsToContents()  # Ajustar tamaño de columnas
        for i in range(3):
            self.table.setColumnWidth(i, max(100, self.table.columnWidth(i)))
        
        layout.addWidget(self.table)
        self.setLayout(layout)
