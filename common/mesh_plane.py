import numpy as np
from .constants import RE, OBLIQUITY_ECLIPTIC
from .rotate import rotate_pqw2eci


def Earth_Mesh():
    u = np.linspace(0, 2*np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    u, v = np.meshgrid(u, v)

    xE = RE*np.cos(u)*np.sin(v)
    yE = RE*np.sin(u)*np.sin(v)
    zE = RE*np.cos(v)
    return np.array([xE, yE, zE])

def Satellite_Mesh(ratio):
    Earth = Earth_Mesh()
    return Earth*ratio

def Equatorial_Plane():
    R_EQ = np.linspace(0, 10*RE, 50)
    t_EQ = np.linspace(0, 2*np.pi, 100)
    R_EQ_grid, t_EQ_grid = np.meshgrid(R_EQ, t_EQ)

    xEQ = R_EQ_grid*np.cos(t_EQ_grid)
    yEQ = R_EQ_grid*np.sin(t_EQ_grid)
    zEQ = np.zeros_like(xEQ)
    return np.array([xEQ, yEQ, zEQ])

def Ecliptic_Plane():
    coe = np.cos(OBLIQUITY_ECLIPTIC)
    soe = np.sin(OBLIQUITY_ECLIPTIC)
    
    xyzEQ = Equatorial_Plane()
    xEL = xyzEQ[0]
    yEL = xyzEQ[1]*coe - xyzEQ[2]*soe
    zEL = xyzEQ[1]*soe - xyzEQ[2]*coe
    return np.array([xEL, yEL, zEL])

def Orbital_Plane(i, RAAN, w):
    xyzEQ = Equatorial_Plane()
    xyzEQ_flatten = np.vstack((xyzEQ[0].flatten(), xyzEQ[1].flatten(), xyzEQ[2].flatten()))
    xyzOR_flatten = rotate_pqw2eci(xyzEQ_flatten, i, RAAN, w)
    
    xOR = xyzOR_flatten[0, :].reshape(xyzEQ[0].shape)
    yOR = xyzOR_flatten[1, :].reshape(xyzEQ[1].shape)
    zOR = xyzOR_flatten[2, :].reshape(xyzEQ[2].shape)
    return np.array([xOR, yOR, zOR])

