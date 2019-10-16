from matplotlib.patches import Circle


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
        self.circle = Circle((coordinates[0], coordinates[1]), mass / 100, color=self.color)

    def create_circle(self):
        self.circle = Circle((self.coordinates[0], self.coordinates[1]), self.mass / 100, color=self.color)


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
