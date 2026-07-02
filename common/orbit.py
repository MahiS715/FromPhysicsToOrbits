import numpy as np
from .constants import MU_EARTH


def orbit_2d(t, state):
    x, y, vx, vy = state
    r_mag = np.sqrt(x**2 + y**2)
    return [vx, vy, -MU_EARTH*x/r_mag**3, -MU_EARTH*y/r_mag**3]