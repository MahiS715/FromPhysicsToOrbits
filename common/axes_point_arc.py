import numpy as np
from .constants import RE
from .rotate import rotate_pqw2eci, rotate_axis


ptI = np.array([10*RE, 0, 0])
ptJ = np.array([0, 10*RE, 0])
ptK = np.array([0, 0, 10*RE])

def ptAN(RAAN):
    return np.array([10*RE*np.cos(RAAN), 10*RE*np.sin(RAAN), 0])

def pth(i, RAAN, w):
    return rotate_pqw2eci(ptK, i, RAAN, w)
def pte(i, RAAN, w):
    return rotate_pqw2eci(ptI, i, RAAN, w)

# def ptTA(t0):
#     return np.array([])

R_arc = 2*RE
def arcRAAN(RAAN):
    tRAAN = np.linspace(0, RAAN, 100)
    xRAAN = R_arc*np.cos(tRAAN)
    yRAAN = R_arc*np.sin(tRAAN)
    zRAAN = np.zeros_like(xRAAN)
    return np.array([xRAAN, yRAAN, zRAAN])

def arci(i, RAAN):
    ti = np.linspace(0, i, 100)
    return rotate_axis(ti, ptAN(RAAN), ptK/5)
def arcw(i, RAAN, w):
    tw = np.linspace(0, w, 100)
    return rotate_axis(tw, pth(i, RAAN, w), ptAN(RAAN)/5)