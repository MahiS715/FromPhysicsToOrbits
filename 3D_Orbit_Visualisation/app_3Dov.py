from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
ROOT_common = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT_common))

import streamlit as st
import numpy as np
import plotly.graph_objects as go


from common.orbit import orbit_2d_eqn_perifocal
from common.rotate import rotate_pqw2eci
from common.axes_point_arc import ptI, ptJ, ptK, pth, arci, ptAN, arcRAAN, pte, arcw
from common.mesh_plane import Earth_Mesh, Satellite_Mesh, Equatorial_Plane, Ecliptic_Plane, Orbital_Plane


st.title("3D Orbit Visualiser")
st.write("Enter the Orbital Elements to Plot any Closed Orbit around Earth")

st.write("")

t = np.linspace(0, 2*np.pi, 1000)

fig = go.Figure()
fig.add_trace(go.Scatter3d(x=[0, ptI[0]], y=[0, ptI[1]], z=[0, ptI[2]], 
                           mode='lines', line=dict(color="red"), name='X Axis (Vernal Equinox)', legendgroup='ICA'))
fig.add_trace(go.Scatter3d(x=[0, ptJ[0]], y=[0, ptJ[1]], z=[0, ptJ[2]], 
                           mode='lines', line=dict(color="green"), name='Y Axis', legendgroup='ICA'))
fig.add_trace(go.Scatter3d(x=[0, ptK[0]], y=[0, ptK[1]], z=[0, ptK[2]],
                           mode='lines', line=dict(color="blue"), name='Z Axis (North Pole)', legendgroup='ICA'))

Earth = Earth_Mesh()
Satellite = Satellite_Mesh(5e-2)
Eq_Plane = Equatorial_Plane()
Ec_Plane = Ecliptic_Plane()

fig.add_trace(go.Surface(x=Earth[0], y=Earth[1], z=Earth[2], 
                         showscale=False, 
                         colorscale=[[0, "royalblue"], [1, "royalblue"]]))

with st.form("Visualisation Input"):
    col1, col2, col3 = st.columns(3)
    with col1:
        a_km = st.number_input("Semi Major Axis - a (km)", value=26564.0, min_value=0.0, step=0.01)
        e = st.number_input("Eccentricity - e", max_value=0.9999, min_value=0.0, value=0.7411, step=0.01, format="%.4f")
        a = a_km*1e3

    with col2:
        i_deg = st.number_input("Inclination - i (deg)", min_value=0.00, max_value=180.00, value=63.40, step=0.01)
        RAAN_deg = st.number_input("RAAN - Ω (deg)", min_value=0.00, max_value=360.00, value=50.00, step=0.01)
        i = np.deg2rad(i_deg)
        RAAN = np.deg2rad(RAAN_deg)

    with col3:
        w_deg = st.number_input("Argument of Perigee - ω (deg)", min_value=0.00, max_value=360.00, value=270.00, step=0.01)
        t0_deg = st.number_input("True Anomaly at Epoch - t₀ (deg)", min_value=0.00, max_value=360.00, value=180.00, step=0.01)
        w = np.deg2rad(w_deg)
        t0 = np.deg2rad(t0_deg)
    p = a*(1 - e**2)

    visualise = st.form_submit_button(label="Visualise", help="Click to Visualise your Orbit")

if visualise:
    r_pqw = orbit_2d_eqn_perifocal(p, e, t)
    r_t0_pqw = orbit_2d_eqn_perifocal(p, e, t0)

    r_eci = rotate_pqw2eci(r_pqw, i, RAAN, w)
    r_t0_eci = rotate_pqw2eci(r_t0_pqw, i, RAAN, w)

    pt_h = pth(i, RAAN, w)
    arc_i = arci(i, RAAN)
    pt_AN = ptAN(RAAN)
    arc_RAAN = arcRAAN(RAAN)
    pt_e = pte(i, RAAN, w)
    arc_w = arcw(i, RAAN, w)

    fig.add_trace(go.Scatter3d(x=[0, pt_h[0]], y=[0, pt_h[1]], z=[0, pt_h[2]],
                               mode='lines', line=dict(color="magenta"), name='Angular Momentum (Direction)', visible='legendonly', legendgroup='AM_Incl'))
    fig.add_trace(go.Scatter3d(x=arc_i[0, :], y=arc_i[1, :], z=arc_i[2, :],
                               mode='lines', line=dict(color="magenta"), name=f'Inclination: {np.rad2deg(i)}°', visible='legendonly', legendgroup='AM_Incl'))
    
    fig.add_trace(go.Scatter3d(x=[0, pt_AN[0]], y=[0, pt_AN[1]], z=[0, pt_AN[2]],
                            mode='lines', line=dict(color="lime"), name='Ascending Node', visible='legendonly', legendgroup='AN_RAAN_Ecc_AP'))
    fig.add_trace(go.Scatter3d(x=arc_RAAN[0, :], y=arc_RAAN[1, :], z=arc_RAAN[2, :],
                            mode='lines', line=dict(color="lime"), name=f'RAAN: {np.rad2deg(RAAN)}°', visible='legendonly', legendgroup='AN_RAAN_Ecc_AP'))
    fig.add_trace(go.Scatter3d(x=[0, pt_e[0]], y=[0, pt_e[1]], z=[0, pt_e[2]],
                            mode='lines', line=dict(color="orange"), name='Eccentricity (Direction)', visible='legendonly', legendgroup='AN_RAAN_Ecc_AP'))
    fig.add_trace(go.Scatter3d(x=arc_w[0, :], y=arc_w[1, :], z=arc_w[2, :],
                            mode='lines', line=dict(color="orange"), name=f'Argument of Perigee: {np.rad2deg(w)}°', visible='legendonly', legendgroup='AN_RAAN_Ecc_AP'))

    fig.add_trace(go.Scatter3d(x=[0, r_t0_eci[0][0]], y=[0, r_t0_eci[1][0]], z=[0, r_t0_eci[2][0]],
                               mode='lines', name='Radius Vector (Satellite)', line=dict(color="yellow")))
    
    fig.add_trace(go.Surface(x=Satellite[0] + r_t0_eci[0], y=Satellite[1] + r_t0_eci[1], z=Satellite[2] + r_t0_eci[2],
                            showscale=False,
                            colorscale=[[0, 'yellow'], [1, 'yellow']],
                            showlegend=True,
                            name='Satellite'))
    
    fig.add_trace(go.Surface(x=Eq_Plane[0], y=Eq_Plane[1], z=Eq_Plane[2],
                            showscale=False,
                            opacity=0.3,
                            colorscale=[[0, "rgba(180,180,180,0.15)"], [1, "rgba(180,180,180,0.15)"]],
                            name="Equatorial Plane",
                            showlegend=True))

    fig.add_trace(go.Surface(x=Ec_Plane[0], y=Ec_Plane[1], z=Ec_Plane[2],
                            showscale=False,
                            opacity=0.3,
                            colorscale=[[0, 'rgba(255,220,100,0.18)'], [1, 'rgba(255,220,100,0.18)']],
                            name="Ecliptic Plane",
                            showlegend=True))
    
    Or_Plane = Orbital_Plane(i, RAAN, w)
    fig.add_trace(go.Surface(x=Or_Plane[0], y=Or_Plane[1], z=Or_Plane[2],
                            showscale=False,
                            opacity=0.3,
                            colorscale=[[0, 'rgba(140,140,255,0.20)'], [1, 'rgba(140,140,255,0.20)']],
                            name="Orbital Plane",
                            showlegend=True,
                            visible='legendonly'))

    fig.add_trace(go.Scatter3d(x=r_eci[0, :], y=r_eci[1, :], z=r_eci[2, :], 
                            mode='lines', name='Orbit',
                            line=dict(width=3, color='white')))
    
    fig.update_layout(
        margin=dict(l=0, r=75, t=25, b=0),
        scene=dict(
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False),
                zaxis=dict(showgrid=False, zeroline=False, visible=False),
                aspectmode='data'),
                paper_bgcolor="black",
                legend=dict(font=dict(color="white"), bordercolor='white', title=" "))
    
    st.plotly_chart(fig)
    st.info("Please use Full Screen to Visualise Propagated Orbit\n\nAny Element can be Selected or Deselected by Clicking them in the Legend")
