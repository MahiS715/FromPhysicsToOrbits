import numpy as np
from .constants import MU_EARTH


def orbit_2d(t, state):
    x, y, vx, vy = state
    r_mag = np.sqrt(x**2 + y**2)
    return [vx, vy, -MU_EARTH*x/r_mag**3, -MU_EARTH*y/r_mag**3]

def orbit_3d(t, state3d):
    x, y, z, vx, vy, vz = state3d
    r_mag = np.sqrt(x**2 + y**2 + z**2)
    return [vx, vy, vz, -MU_EARTH*x/r_mag**3, -MU_EARTH*y/r_mag**3, -MU_EARTH*z/r_mag**3]

def orbit_2d_eqn_perifocal(p, e, t):
    r = p/(1 + e*np.cos(t))
    x = r*np.cos(t)
    y = r*np.sin(t)
    return np.vstack((x, y, np.zeros_like(x)))