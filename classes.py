class Particle:
    """
    Class describing a single particle
    """
    def __init__(self, coordinates=[0, 0], speed=[0, 0], mass=1, color="red", living_time=1):
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
        self.emitting_vector = emitting_vector
