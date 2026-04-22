import sys
from PyQt6.QtWidgets import QApplication
from backend import Backend
from ui.login import LoginScreen


def main():
    app = QApplication(sys.argv)
    backend = Backend()
    login = LoginScreen(backend)
    login.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
