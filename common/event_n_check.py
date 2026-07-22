from .constants import RE
import numpy as np
import streamlit as st

def launch_position(r_vec):
    if np.linalg.norm(r_vec) <= RE:
        st.error("Satellite can't be launched from Underground! \nCheck Your Position Input")
        st.stop()

def crash_detect_2d(t, state2d):
    x, y, vx, vy = state2d
    r_mag = np.sqrt(x**2 + y**2)
    return r_mag - RE

def crash_detect_3d(t, state3d):
    x, y, z, vx, vy, vz = state3d
    r_mag = np.sqrt(x**2 + y**2 + z**2)
    return r_mag - RE