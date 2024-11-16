from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from menu import MenuWindow

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initialize_menu()

    def initialize_menu(self):
        self.menu = MenuWindow()
        self.menu.show()

def main():
    """Función principal que inicia la aplicación."""
    app = QApplication(sys.argv)
    main_app = MainApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()