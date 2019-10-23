from scipy.integrate import odeint
import numpy as np
import math


G = 6.67408 * math.pow(10, -11)


def get_acceleration(particleList, index):
    """
    Getting acceleration for one point dictated by other points
    """
    res = np.array([0.0, 0.0])

    for i in range(len(particleList)):
        if i == index:
            continue

        distance = np.array([particleList[i].coordinates[0] - particleList[index].coordinates[0],
                             particleList[i].coordinates[1] - particleList[index].coordinates[1]])

        res += G * particleList[i].mass * distance / (np.linalg.norm(distance) ** 3)

    return res


def pend(prev, t, particleList, index):
    x, y, u, v = prev
    summ_x, summ_y = get_acceleration(particleList, index)
    return [u, v, summ_x, summ_y]


def calculate_odeint(particleList, delta_t):
    """
    Calculation based on odeint
    """
    new_particles = particleList.copy()
    to_delete = []

    if len(particleList) == 1:
        new_particles[0].living_time -= 1

        if new_particles[0].living_time == 0:
            del new_particles[0]
            return new_particles

        new_particles[0].coordinates[0] += particleList[0].speed[0]
        new_particles[0].coordinates[1] += particleList[0].speed[1]
        return new_particles

    for i in range(len(particleList)):
        new_particles[i].living_time -= 1

        if new_particles[i].living_time == 0:
            to_delete.append(i)
            continue

        res = odeint(func=pend,
                     y0=[
                        particleList[i].coordinates[0],
                        particleList[i].coordinates[1],
                        particleList[i].speed[0],
                        particleList[i].speed[1]
                     ],
                     t=np.linspace(0, delta_t, 2),
                     args=(particleList, i))

        new_particles[i].coordinates[0], new_particles[i].coordinates[1], new_particles[i].speed[0], new_particles[i].speed[1] = res[-1]

    while len(to_delete) > 0:
        del new_particles[to_delete[0]]
        to_delete = [ elem - 1 if elem > to_delete[0] else elem for elem in to_delete[1:] ]

    return new_particles


def calculate_verle(particleList, delta_t):
    """
    Calculations based in Verle method
    """

    new_particles = particleList.copy()
    to_delete = []

    if len(particleList) == 1:
        new_particles[0].living_time -= 1

        if new_particles[0].living_time == 0:
            del new_particles[0]
            return new_particles

        new_particles[0].coordinates[0] += particleList[0].speed[0]
        new_particles[0].coordinates[1] += particleList[0].speed[1]
        return new_particles

    for i in range(len(particleList)):
        new_particles[i].living_time -= 1

        if new_particles[i].living_time == 0:
            to_delete.append(i)
            continue

        old_acceleration = get_acceleration(particleList, i)

        new_particles[i].coordinates[0] += (particleList[i].speed[0] + old_acceleration[0] / 2) * delta_t
        new_particles[i].coordinates[1] += (particleList[i].speed[1] + old_acceleration[1] / 2) * delta_t

        new_acceleration = get_acceleration(new_particles, i)

        new_particles[i].speed[0] += (new_acceleration[0] + old_acceleration[0]) / 2 * delta_t
        new_particles[i].speed[1] += (new_acceleration[1] + old_acceleration[1]) / 2 * delta_t

    while len(to_delete) > 0:
        del new_particles[to_delete[0]]
        to_delete = [ elem - 1 if elem > to_delete[0] else elem for elem in to_delete[1:] ]

    return new_particles
