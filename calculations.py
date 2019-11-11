from scipy.integrate import odeint
import numpy as np
import math
from classes import Particle
import copy


G = 6.6743015 * (10 ** -11)


def supercopy(lst):
    result = []

    for elem in lst:
        newParticle = Particle(
                               [
                                   elem.coordinates[0],
                                   elem.coordinates[1]
                               ],
                               [
                                   elem.speed[0],
                                   elem.speed[1]
                               ],
                               elem.mass,
                               elem.color,
                               elem.living_time
                               )
        result.append(newParticle)

    return result


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

        if np.linalg.norm(distance) <= particleList[index].mass * 5 + particleList[i].mass * 5:
            continue

        res += G * particleList[i].mass * distance / (np.linalg.norm(distance) ** 3)

    return res


def pend(prev, t, particleList, index):
    x, y, u, v = prev
    particleList[index].coordinates = [x, y]
    summ_x, summ_y = get_acceleration(particleList, index)
    return [u, v, summ_x, summ_y]


def calculate_odeint(particleList, delta_t):
    """
    Calculation based on odeint
    """
    new_particles = supercopy(particleList)
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

        y0 = copy.deepcopy([
                  particleList[i].coordinates[0],
                  particleList[i].coordinates[1],
                  particleList[i].speed[0],
                  particleList[i].speed[1]
             ])

        res = odeint(func=pend,
                     y0=y0,
                     t=np.linspace(0, delta_t, 2),
                     args=(new_particles, i))

        new_particles[i].coordinates[0], new_particles[i].coordinates[1], new_particles[i].speed[0], new_particles[i].speed[1] = res[-1]

    while len(to_delete) > 0:
        del new_particles[to_delete[0]]
        to_delete = [ elem - 1 if elem > to_delete[0] else elem for elem in to_delete[1:] ]

    return new_particles


def calculate_verle(particleList, delta_t):
    """
    Calculations based in Verle method
    """

    new_particles = supercopy(particleList)
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


def overall_pend(prev, t, p_masses):
    acceleration_list = []

    for i in range(len(prev) // 4):
        partial_acceleration = np.array([0.0, 0.0])

        for j in range(len(prev) // 4):
            if i == j:
                continue

            distance = np.array([
                                    prev[i * 4] - prev[j * 4],
                                    prev[i * 4 + 1] - prev[j * 4 + 1]
                                ])

            norm = np.linalg.norm(distance)

            if norm <= p_masses[i] * 5 + p_masses[j] * 5:
                continue

            partial_acceleration += G * p_masses[j] * distance / norm

        acceleration_list.append([partial_acceleration[0], partial_acceleration[1]])

    result = []

    for i in range(len(prev) // 4):
        result.extend([
                          prev[i * 4 + 2],
                          prev[i * 4 + 3],
                          acceleration_list[i][0],
                          acceleration_list[i][1]
                      ])

    return result


def overall_odeint(particleList, tGrid):
    particles = []

    y0 = []

    for _, p in enumerate(particleList):
        y0.extend([
                      p.coordinates[0],
                      p.coordinates[1],
                      p.speed[0],
                      p.speed[1]
                  ])

    result = odeint(func=overall_pend, y0=y0, t=tGrid, args=([p.mass for _, p in enumerate(particleList)],))

    for i in range(len(result[-1]) // 4):
        particles.append([
                             result[-1][i * 4],
                             result[-1][i * 4 + 1],
                             result[-1][i * 4 + 2],
                             result[-1][i * 4 + 3],
                         ])

    return particles


def overall_verle(particleList, tGrid):
    particles = [[
                     p.coordinates[0],
                     p.coordinates[1],
                     p.speed[0],
                     p.speed[1]] for p in particleList
                 ]

    delta_t = tGrid[1] - tGrid[0]

    for _, p in enumerate(particleList):
        particles.append([
                             p.coordinates[0],
                             p.coordinates[1],
                             p.speed[0],
                             p.speed[1]
                         ])


