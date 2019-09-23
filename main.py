import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from .classes import Particle, Emitter


emitter = Emitter()


def generateParticle():
    global form, emitter

    try:
        xAxisSpeed = int(form.particleXAxisSpeedLineEdit.text())
    except Exception:
        print("x axis speed is in wrong format!")
        return

    try:
        yAxisSpeed = int(form.particleYAxisSpeedLineEdit.text())
    except Exception:
        print("y axis speed is in wrong format!")
        return

    particle = Particle(emitter.coordinates, [xAxisSpeed, yAxisSpeed])


if __name__ == "__main__":
    global form

    app = QApplication(sys.argv)

    Form, Window = uic.loadUiType("form.ui")
    window = Window()
    form = Form()
    form.setupUi(window)

    form.generateParticleButton.clicked.connect(generateParticle)

    window.show()
    app.exec_()
