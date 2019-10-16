import sys
from PyQt5.QtWidgets import QApplication
from gui import MyMainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyMainWindow()

    window.show()
    app.exec_()
