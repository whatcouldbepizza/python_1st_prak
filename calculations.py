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


def calculate_odeint(particleList, time):
    """
    Calculation based on odeint
    """
    if len(particleList) == 1:
        particleList[0].coordinates[0] += particleList[0].speed[0]
        particleList[0].coordinates[1] += particleList[0].speed[1]
        return particleList

    for i in range(len(particleList)):
        res = odeint(func=pend,
                     y0=[
                        particleList[i].coordinates[0],
                        particleList[i].coordinates[1],
                        particleList[i].speed[0],
                        particleList[i].speed[1]
                     ],
                     t=np.linspace(time, time + 1, 2),
                     args=(particleList, i))

        particleList[i].coordinates[0], particleList[i].coordinates[1], particleList[i].speed[0], particleList[i].speed[1] = res[-1]

    return particleList