from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.patches import Arrow
from matplotlib.animation import FuncAnimation

import numpy as np

from classes import Particle, Emitter
from calculations import calculate_odeint, calculate_verle

import json
import datetime


Ui_MainWindow, QMainWindow = uic.loadUiType("form.ui")


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

        self.emitter_vector = Arrow(self.emitter.coordinates[0], self.emitter.coordinates[1],
                                    self.emitter.vector[0] / 20, self.emitter.vector[1] / 20, width=0.09)

        self.ax.add_artist(self.emitter_vector)

        self.figure.canvas.mpl_connect('button_press_event', self.changeEmitter)

        self.particleList = self.initialize_solar_system()

        self.animation = FuncAnimation(self.figure, self.draw_particles, interval=500)

        self.time = 0


    def draw_particles(self, frame):
        """
        Function to draw all particles
        """
        if self.pauseRadioButton.isChecked():
            return

        for i in range(len(self.particleList)):
            try:
                self.particleList[i].circle.remove()
            except Exception:
                pass

        start_time = datetime.datetime.now()

        if self.methodCheckBox.isChecked():
            self.particleList = calculate_verle(self.particleList)
            print("Verle iteration time: {}".format(datetime.datetime.now() - start_time))
        else:
            self.particleList = calculate_odeint(self.particleList, self.time)
            print("Odeint iteration time: {}".format(datetime.datetime.now() - start_time))

        if len(self.particleList) != 0:
            max_x = max([ elem.coordinates[0] for elem in self.particleList ])
            max_y = max([ elem.coordinates[1] for elem in self.particleList ])
            max_m = max([ elem.mass for elem in self.particleList ])

            sorted_masses = sorted([ elem.mass for elem in self.particleList ])
            masses_map = dict()
            sizes = np.linspace(0.01, 0.05, len(sorted_masses))

            for i, elem in enumerate(sorted_masses):
                masses_map[elem] = sizes[i]

            for i in range(len(self.particleList)):

                self.particleList[i].create_circle(coordinates=
                                                   [
                                                       self.particleList[i].coordinates[0] / max_x,
                                                       self.particleList[i].coordinates[1] / (max_x / 10)
                                                   ],
                                                   #size=self.particleList[i].mass / (max_m * 10)
                                                   size=masses_map[self.particleList[i].mass],
                                                   color=self.particleList[i].color)

                self.ax.add_artist(self.particleList[i].circle)

        self.time += 1
        self.figure.canvas.draw_idle()


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
        vertical_layout1.addWidget(self.particleColorLineEdit)
        vertical_layout1.addWidget(self.massLabel)
        vertical_layout1.addWidget(self.particleMassSlider)
        vertical_layout1.addWidget(self.generateParticleButton)

        vertical_layout2 = QVBoxLayout()

        vertical_layout2.addWidget(self.emitterXLineEdit)
        vertical_layout2.addWidget(self.emitterYLineEdit)
        vertical_layout2.addWidget(self.emitterXVectorLineEdit)
        vertical_layout2.addWidget(self.emitterYVectorLineEdit)
        vertical_layout2.addWidget(self.emitterChangeButton)
        vertical_layout2.addWidget(self.pauseRadioButton)

        horizontal_layout1 = QHBoxLayout()

        horizontal_layout1.addLayout(vertical_layout1)
        horizontal_layout1.addLayout(vertical_layout2)

        vertical_layout3 = QVBoxLayout()

        vertical_layout3.addLayout(horizontal_layout1)
        vertical_layout3.addWidget(self.methodCheckBox)

        horizontal_layout2 = QHBoxLayout()

        horizontal_layout2.addLayout(vertical_layout3)
        horizontal_layout2.addWidget(self.canvas)

        self.centralwidget.setLayout(horizontal_layout2)


    def generateParticle(self):
        """
        Generate particle button click event handler
        """
        try:
            xAxisSpeed = float(self.particleXAxisSpeedLineEdit.text())
        except Exception:
            print("generateParticle(): x axis speed is in wrong format!")
            return

        try:
            yAxisSpeed = float(self.particleYAxisSpeedLineEdit.text())
        except Exception:
            print("generateParticle(): y axis speed is in wrong format!")
            return

        color = self.particleColorLineEdit.text()

        mass = self.particleMassSlider.value()

        particle = Particle([
                                self.emitter.coordinates[0],
                                self.emitter.coordinates[1]
                            ],
                            [
                                xAxisSpeed * self.emitter.vector[0],
                                yAxisSpeed * self.emitter.vector[1]
                            ],
                            mass,
                            color)

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


    def initialize_solar_system(self, data_file="solar_system.json"):
        """
        Function that prepares solar system example
        """
        with open(data_file, "r") as descr:
            text_content = descr.read()

        json_content = json.loads(text_content)

        for val in json_content["particles"].values():

            particle = Particle(coordinates=[val["x"], val["y"]],
                                speed=[val["u"], val["v"]],
                                mass=val["m"],
                                color=val["color"],
                                living_time=val["lifetime"])

            self.particleList.append(particle)

        return self.particleList
