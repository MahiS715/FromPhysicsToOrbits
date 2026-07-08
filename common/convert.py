import numpy as np
from .constants import MU_EARTH
from .axes_point_arc import ptI, ptJ, ptK


I = ptI/np.linalg.norm(ptI)
J = ptJ/np.linalg.norm(ptJ)
K = ptK/np.linalg.norm(ptK)

def vector2OE(r0, v0):
    r0_mag = np.linalg.norm(r0)
    v0_mag = np.linalg.norm(v0)
    
    sp_E = v0_mag**2/2 - MU_EARTH/r0_mag
    a = -MU_EARTH/(2*sp_E)

    h = np.cross(r0, v0)
    h_cap = h/np.linalg.norm(h)
    n_cap = np.cross(K, h_cap)

    e = np.cross(v0, h)/MU_EARTH - r0/np.linalg.norm(r0)
    e_mag = np.linalg.norm(e)
    e_cap = e/e_mag

    i = np.arccos(np.dot(K, h_cap))
    RAAN = np.arctan2(np.dot(J, n_cap), np.dot(I, n_cap))
    w = np.arccos(np.dot(n_cap, e_cap))
    t0 = np.arccos(np.dot(e_cap, r0)/np.linalg.norm(r0))

    if e[2] < 0:
        w = 2*np.pi - w
    if np.dot(r0, v0) < 0:
        t0 = 2*np.pi - t0
    
    return [a, e_mag, np.rad2deg(i), np.rad2deg(RAAN), np.rad2deg(w), np.rad2deg(t0)]
