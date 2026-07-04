import numpy as np


def rotation_matrix(angle, axis):
    ca = np.cos(angle) 
    sa = np.sin(angle)
    if axis == "x":
        R = np.array([[1, 0, 0],
                      [0, ca, -sa],
                      [0, sa, ca]])
    elif axis == "y":
        R = np.array([[ca, 0, sa],
                      [0, 1, 0],
                      [-sa, 0, ca]])
    elif axis == "z":
        R = np.array([[ca, -sa, 0],
                      [sa, ca, 0],
                      [0, 0, 1]])
    return R

def rotate_pqw2eci(r_pqw, i, RAAN, w):
    R_i = rotation_matrix(i, axis="x")
    R_RAAN = rotation_matrix(RAAN, axis="z")
    R_w = rotation_matrix(w, axis="z")
    return (R_RAAN @ (R_i @ (R_w @ r_pqw)))

def rotate_axis(angle, axis_vec, initial_vec):
    ''' Input Angle can be an array
    The output is a set of Vectors for each Angle input
    Angle Input shall be in Radians
    '''
    initial_vec = np.array(initial_vec)
    rotated_vec = np.zeros((3, angle.shape[0]))
    axis_vec_norm = axis_vec/np.linalg.norm(axis_vec)

    rotated_vec += initial_vec[:, None]*np.cos(angle[None, :])
    rotated_vec += np.cross(axis_vec_norm, initial_vec)[:, None]*np.sin(angle[None, :])
    rotated_vec += axis_vec_norm[:, None]*np.dot(axis_vec_norm, initial_vec)*(1 - np.cos(angle[None, :]))
    return rotated_vec