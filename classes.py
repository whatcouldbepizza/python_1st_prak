from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.patches import Arrow
import multiprocessing


Ui_MainWindow, QMainWindow = uic.loadUiType("form.ui")


class Particle:
    """
    Class describing a single particle
    """
    def __init__(self, coordinates=[0, 0], speed=[0.5, 0.5], mass=1, color="red", living_time=1):
        """
        Main constructor
        """
        self.coordinates = coordinates
        self.speed = speed
        self.mass = mass
        self.color = color
        self.living_time = living_time


class Emitter:
    """
    Class describing emitter
    """
    def __init__(self, coordinates=[0, 0], emitting_vector=[1, 1]):
        """
        Main constructor
        """
        self.coordinates = coordinates
        self.vector = emitting_vector

    def change_position(self, coordinates, vector):
        """
        Function to change position of emitting source
        """
        self.coordinates = coordinates
        self.vector = vector


class MyMainWindow(QMainWindow, Ui_MainWindow):
    """
    Main window class
    """
    def __init__(self, ):
        """
        Main constructor
        """
        super(MyMainWindow, self).__init__()

        self.setupUi(self)
        self.connect_click_handlers()

        self.emitter = Emitter()
        self.particleList = []

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.setLayouts()

        self.ax = self.figure.add_subplot(1, 1, 1)

        #self.emitter_circle = plt.Circle((self.emitter.coordinates[0], self.emitter.coordinates[1]), 0.05, color='r')
        self.emitter_vector = Arrow(self.emitter.coordinates[0], self.emitter.coordinates[1],
                                    self.emitter.vector[0] / 20, self.emitter.vector[1] / 20, width=0.09)

        #ax.add_artist(self.emitter_circle)
        self.ax.add_artist(self.emitter_vector)

        self.figure.canvas.mpl_connect('button_press_event', self.changeEmitter)




    def connect_click_handlers(self):
        """
        Function that connects button click events to proper handlers
        """
        self.generateParticleButton.clicked.connect(self.generateParticle)
        self.emitterChangeButton.clicked.connect(self.changeEmitter)


    def setLayouts(self):
        vertical_layout1 = QVBoxLayout()

        vertical_layout1.addWidget(self.particleXAxisSpeedLineEdit)
        vertical_layout1.addWidget(self.particleYAxisSpeedLineEdit)
        vertical_layout1.addWidget(self.massLabel)
        vertical_layout1.addWidget(self.particleMassSlider)
        vertical_layout1.addWidget(self.generateParticleButton)

        vertical_layout2 = QVBoxLayout()

        vertical_layout2.addWidget(self.emitterXLineEdit)
        vertical_layout2.addWidget(self.emitterYLineEdit)
        vertical_layout2.addWidget(self.emitterXVectorLineEdit)
        vertical_layout2.addWidget(self.emitterYVectorLineEdit)
        vertical_layout2.addWidget(self.emitterChangeButton)

        horizontal_layout = QHBoxLayout()

        horizontal_layout.addLayout(vertical_layout1)
        horizontal_layout.addLayout(vertical_layout2)
        horizontal_layout.addWidget(self.canvas)

        self.centralwidget.setLayout(horizontal_layout)


    def generateParticle(self):
        """
        Generate particle button click event handler
        """
        try:
            xAxisSpeed = int(self.particleXAxisSpeedLineEdit.text())
        except Exception:
            print("generateParticle(): x axis speed is in wrong format!")
            return

        try:
            yAxisSpeed = int(self.particleYAxisSpeedLineEdit.text())
        except Exception:
            print("generateParticle(): y axis speed is in wrong format!")
            return

        mass = self.particleMassSlider.value()

        particle = Particle(self.emitter.coordinates, [xAxisSpeed, yAxisSpeed], mass)

        self.particleList.append(particle)


    def changeEmitter(self):
        """
        Emitter position changed button click event handler
        """
        # ------------------------ Parsing new valus ---------------------------
        try:
            xAxis = float(self.emitterXLineEdit.text())
        except Exception:
            print("changeEmitter(): x axis is in wrong format!")
            return

        try:
            yAxis = float(self.emitterYLineEdit.text())
        except Exception:
            print("changeEmitter(): y axis is in wrong format!")
            return

        try:
            xVector = int(self.emitterXVectorLineEdit.text())
        except Exception:
            print("changeEmitter(): x axis vector is in wrong format!")
            return

        try:
            yVector = int(self.emitterYVectorLineEdit.text())
        except Exception:
            print("changeEmitter(): y axis vector is in wrong format!")
            return
        # -----------------------------------------------------------------------

        # Changing emitter position
        self.emitter.change_position([xAxis, yAxis], [xVector, yVector])

        # Removing old emitter (we have no emitter, don't do anything)
        try:
            self.emitter_vector.remove()
        except Exception:
            pass

        # Creating new emitter
        self.emitter_vector = Arrow(self.emitter.coordinates[0], self.emitter.coordinates[1],
                                    self.emitter.vector[0] / 20, self.emitter.vector[1] / 20, width=0.09)
        # Adding it to the plot
        self.ax.add_artist(self.emitter_vector)

        # Redraw plot
        self.figure.canvas.draw_idle()

