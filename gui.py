from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.patches import Arrow
from matplotlib.animation import FuncAnimation

import numpy as np
from math import pow

from classes import Particle, Emitter
from calculations import calculate_odeint, calculate_verle, supercopy

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

        self.figure.canvas.mpl_connect('button_press_event', self.changeEmitter)

        self.solar_mode = False

        self.particleList = self.initialize_solar_system()
        self.particleListV = supercopy(self.particleList)

        self.animation = FuncAnimation(self.figure, self.draw_particles, interval=10)

        self.x_scale = None

        self.inaccuracy_iter = [[], []]
        self.i = 0


    def draw_particles(self, frame):
        """
        Function to draw all particles
        """
        if self.pauseRadioButton.isChecked():
            return

        self.i += 1

        for i in range(len(self.particleList)):
            try:
                self.particleList[i].circle.remove()
            except Exception:
                pass

        delta_t = 10 if self.solar_mode else 1

        odeint_list = supercopy(self.particleList)
        verle_list = supercopy(self.particleListV)

        #if self.methodCheckBox.isChecked():
            #self.particleList = calculate_verle(self.particleList, delta_t)
        #    verle_list = calculate_verle(verle_list, delta_t)
            #print("Verle iteration time: {}".format(datetime.datetime.now() - start_time))
        #else:
            #self.particleList = calculate_odeint(self.particleList, delta_t)
        #    odeint_list = calculate_odeint(odeint_list, delta_t)
            #print("Odeint iteration time: {}".format(datetime.datetime.now() - start_time))

        start_time = datetime.datetime.now()
        verle_list = calculate_verle(verle_list, delta_t)
        print("Verle iteration: {}".format(datetime.datetime.now() - start_time))

        start_time = datetime.datetime.now()
        odeint_list = calculate_odeint(odeint_list, delta_t)
        print("Odeint iteration: {}".format(datetime.datetime.now() - start_time))

        self.particleList = supercopy(odeint_list)
        self.particleListV = supercopy(verle_list)

        metric = .0

        for p_1, p_2 in zip(odeint_list, verle_list):
            dist = np.array(p_1.coordinates) - np.array(p_2.coordinates)
            metric += np.linalg.norm(dist)

        self.inaccuracy_iter[0].append(self.i)
        self.inaccuracy_iter[1].append(metric)

        if len(self.particleList) != 0:

            if self.x_scale is None:
                self.x_scale = max([ elem.coordinates[0] for elem in self.particleList ] + [100])
            max_m = max([ elem.mass for elem in self.particleList ])

            sorted_masses = sorted([ elem.mass for elem in self.particleList ])
            masses_map = dict()
            sizes = np.linspace(0.01, 0.03, len(sorted_masses))

            for i, elem in enumerate(sorted_masses):
                masses_map[elem] = sizes[i]

            for i in range(len(self.particleList)):

                self.particleList[i].create_circle(coordinates=
                                                   [
                                                       self.particleList[i].coordinates[0] / (self.x_scale * 2.1) + 0.5,
                                                       self.particleList[i].coordinates[1] / (self.x_scale * 2.1) + 0.5
                                                   ],
                                                   size=masses_map[self.particleList[i].mass],
                                                   color=self.particleList[i].color)

                self.ax.add_artist(self.particleList[i].circle)

        self.figure.canvas.draw_idle()


    def connect_click_handlers(self):
        """
        Function that connects button click events to proper handlers
        """
        self.generateParticleButton.clicked.connect(self.generateParticle)
        self.emitterChangeButton.clicked.connect(self.changeEmitter)
        self.pauseRadioButton.clicked.connect(self.draw_inacc)


    def draw_inacc(self):
        plt.plot(self.inaccuracy_iter[0], self.inaccuracy_iter[1])


    def setLayouts(self):
        vertical_layout1 = QVBoxLayout()

        vertical_layout1.addWidget(self.particleXAxisSpeedLineEdit)
        vertical_layout1.addWidget(self.particleYAxisSpeedLineEdit)
        vertical_layout1.addWidget(self.particleColorLineEdit)
        vertical_layout1.addWidget(self.massLabel)
        vertical_layout1.addWidget(self.particleMassLineEdit)
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
        self.canvas.setMinimumWidth(700)
        self.canvas.setMinimumHeight(700)
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

        #mass = self.particleMassSlider.value()

        try:
            mass_list = self.particleMassLineEdit.text().upper().split('E')
            mass = float(mass_list[0]) * pow(10, int(mass_list[1]))
        except Exception as ex:
            print("generateParticle(): failed to parse mass, error: " + str(ex))
            return

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
        self.x_scale = None


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

        # Redraw plot
        self.figure.canvas.draw_idle()


    def initialize_solar_system(self, data_file="solar_system.json"):
        """
        Function that prepares solar system example
        """
        self.particleList = []

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

        self.solar_mode = True

        return self.particleList


    def print_particle_list(self, lst=None):
        for elem in lst:
            print(elem.coordinates)

        print("-----")
