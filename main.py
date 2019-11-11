import sys
from PyQt5.QtWidgets import QApplication
from gui import MyMainWindow
from compare import compare


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyMainWindow()

    if sys.argv[1] == "compare":
        particleList = window.initialize_solar_system()
        compare(particleList)
    else:
        window.show()
        app.exec_()
