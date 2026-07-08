from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
ROOT_common = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT_common))

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import solve_ivp
import time
import pandas as pd

from common.orbit import orbit_3d
from common.mesh_plane import Earth_Mesh
from common.animate import play_button, pause_button, reset_opt
from common.convert import vector2OE

if "input_received" not in st.session_state:
    st.session_state.input_received = False
if "orbit_animation_status" not in st.session_state:
    st.session_state.orbit_animation_status = False
if "input_data" not in st.session_state:
    st.session_state.input_data = None

Earth = Earth_Mesh()

conversion_to_seconds = {"sec": 1,
                        "min": 60,
                        "hr": 60*60,
                        "day": 24*60*60,
                        "yr": 365.25*24*60*60}

st.title("Orbital Maneuver")

tab_anim, tab_oe= st.tabs(["Maneuver Animation", "Orbital Elements"])

with tab_anim:
    st.info("Enter the Initial Radius and Velocity Vector to Find your Satellite's Orbit around Earth")

    st.write("")

    with st.form("Maneuver_Input"):
        colr, colv, colt = st.columns([2, 2, 3])
        with colr:
            st.latex(r"\text{Radius Vector}")
            r0_x = st.number_input("X Component (km)", value=7000.0, step=100.0)
            r0_y = st.number_input("Y Component (km)", value=0.0, step=100.0)
            r0_z = st.number_input("Z Component (km)", value=0.0, step=100.0)

        with colv:
            st.latex(r"\text{Velocity Vector}")
            v0_x = st.number_input("X Component (km/s)", value=0.0000, step=0.1, format="%.4f")
            v0_y = st.number_input("Y Component (km/s)", value=7.5000, step=0.1, format="%.4f")
            v0_z = st.number_input("Z Component (km/s)", value=0.0000, step=0.1, format="%.4f")

        with colt:
            st.latex(r"\text{Simulation Parameters}")
            colt1, colt2 = st.columns(2)
            with colt1:
                tf_val = st.number_input("Simulation Time", min_value=1.0, max_value=60.0, value=1.0, step=1.0)
                tf_unit = st.selectbox("Time Unit", ["sec", "min", "hr", "day"], index=3)
                tf = tf_val*conversion_to_seconds[tf_unit]

            with colt2:
                t_maneuver = st.number_input("Maneuver Time", min_value=1.0, max_value=60.0, value=17.0, step=1.0)
                t_maneuver_unit = st.selectbox("Time Unit", ["sec", "min", "hr", "day"], index=2)
                t_maneuver_sec = t_maneuver*conversion_to_seconds[t_maneuver_unit]

            if t_maneuver_sec > tf:
                st.warning("Maneuver can't be done Beyond Simulation Time - Might produce Unwanted Behaviour")

            req_points_pre_maneuver = max(1500, int(t_maneuver_sec/200))
            num_points_pre_maneuver = min(50000, req_points_pre_maneuver)
            req_points_post_maneuver = max(1500, int((tf - t_maneuver_sec)/200))
            num_points_post_maneuver = min(50000, req_points_post_maneuver)

            teval_pre_maneuver = np.linspace(0, t_maneuver_sec, num_points_pre_maneuver)
            teval_post_maneuver = np.linspace(t_maneuver_sec, tf, num_points_post_maneuver)

        st.latex(r"\text{Maneuver - Velocity Change } \Delta v")

        colm1, colm2, colm3 = st.columns(3)
        with colm1:
            del_v_x = st.number_input("(Δv) X Component (km/s)", value=2.0000, step=0.1, format="%.4f")
        with colm2:
            del_v_y = st.number_input("(Δv) Y Component (km/s)", value=0.0000, step=0.1, format="%.4f")
        with colm3:
            del_v_z = st.number_input("(Δv) Z Component (km/s)", value=0.0000, step=0.1, format="%.4f")
        

        maneuver = st.form_submit_button(label="Maneuver", help="Click to Maneuver your Probe")

    if maneuver:
        colm3, colm4 = st.columns([7, 3])
        with colm3:
            st.write("")
        with colm4:
            st.success(f"No of Points used: {num_points_pre_maneuver + num_points_post_maneuver}")

        r0 = np.array([r0_x, r0_y, r0_z])*1e3
        v0 = np.array([v0_x, v0_y, v0_z])*1e3

        del_vm = np.array([del_v_x, del_v_y, del_v_z])*1e3
        st.session_state.input_received = True

        with st.spinner("Solving the Maneuver...", show_time=True):
            start = time.perf_counter()
            sol_pre_maneuver = solve_ivp(orbit_3d, t_span=[0, t_maneuver_sec], y0=np.concatenate((r0, v0)), t_eval=teval_pre_maneuver,
                                         method="DOP853", dense_output=False,
                                         rtol=1e-8, atol=1e-10)
            
            r0m = np.array([sol_pre_maneuver.y[0, -1], sol_pre_maneuver.y[1, -1], sol_pre_maneuver.y[2, -1]])
            v0m = np.array([sol_pre_maneuver.y[3, -1], sol_pre_maneuver.y[4, -1], sol_pre_maneuver.y[5, -1]]) + del_vm
            sol_post_maneuver = solve_ivp(orbit_3d, t_span=[t_maneuver_sec, tf], y0=np.concatenate((r0m, v0m)), t_eval=teval_post_maneuver,
                                          method="DOP853", dense_output=False,
                                          rtol=1e-8, atol=1e-10)

            elapsed = time.perf_counter() - start
        st.metric("Simulation Time", f"{elapsed:.3f} s")

        st.session_state.input_data = [r0, v0, r0m, v0m]

        with st.spinner("Animating...", show_time=True):
            fig_anim = go.Figure(data=[go.Scatter3d(x=[sol_pre_maneuver.y[0, 0]], y=[sol_pre_maneuver.y[1, 0]], z=[sol_pre_maneuver.y[2, 0]], mode="markers", name="Satellite", marker=dict(size=3, color='white'))])
            fig_anim.add_trace(go.Surface(x=Earth[0], y=Earth[1], z=Earth[2],
                                    showscale=False, colorscale=[[0, "royalblue"], [1, "royalblue"]]))
            fig_anim.add_trace(go.Scatter3d(x=sol_pre_maneuver.y[0], y= sol_pre_maneuver.y[1], z=sol_pre_maneuver.y[2],
                                    mode="lines", name="Orbit - PreManeuver", line=dict(color="white"), opacity=0.25))
            fig_anim.add_trace(go.Scatter3d(x=sol_post_maneuver.y[0], y= sol_post_maneuver.y[1], z=sol_post_maneuver.y[2],
                                    mode="lines", name="Orbit - PostManeuver", line=dict(color="orange"), opacity=0.25))

            frames_pre_maneuver = [go.Frame(data=[go.Scatter3d(x=[sol_pre_maneuver.y[0, i]], y=[sol_pre_maneuver.y[1, i]], z=[sol_pre_maneuver.y[2, i]], mode="markers", marker=dict(size=3, color="white"))], traces=[0], name=f"pre_{i}", layout=go.Layout())
                                                for i in range(0, num_points_pre_maneuver, 5)]
            frames_post_maneuver = [go.Frame(data=[go.Scatter3d(x=[sol_post_maneuver.y[0, i]], y=[sol_post_maneuver.y[1, i]], z=[sol_post_maneuver.y[2, i]], mode="markers", marker=dict(size=3, color="orange"))], traces=[0], name=f"post_{i}", layout=go.Layout())
                                                for i in range(0, num_points_post_maneuver, 5)]
            frames = frames_pre_maneuver + frames_post_maneuver
            no_frames = len(frames)
            st.write(f"No of Frames: {no_frames}")

            st.info("Pause to Change your View Angle :)")
            fig_anim.frames = frames
            reset_button = dict(label="   Reset   ", method="animate", args=[["pre_0"], reset_opt])
            fig_anim.update_layout(scene=dict(xaxis=dict(showgrid=False, zeroline=False, visible=False),
                                              yaxis=dict(showgrid=False, zeroline=False, visible=False),
                                              zaxis=dict(showgrid=False, zeroline=False, visible=False),
                                              aspectmode="data", uirevision="constant"),
                                    legend=dict(font=dict(color="white")),
                                    updatemenus=[dict(type="buttons", showactive=False, 
                                                        direction="left", x=0.5, xanchor="center", y=-0.1, yanchor="top",
                                                        buttons=[play_button, pause_button, reset_button])])

            st.plotly_chart(fig_anim, config=dict(displayModeBar=False), key=f"anim_{time.time()}")

            st.warning("Do Not Re-Run this Streamlit App - Might cause Animation Issues!")


with tab_oe:
    if not st.session_state.input_received:
        st.warning("Maneuver the Orbit in Tab 1 First")
        st.stop()
    
    orbit_data = st.session_state.input_data

    with st.expander(label="Input Data", expanded=False):
        st.latex(r"\text{Initial Radius Vector: }" + fr"[{r0_x} \quad {r0_y} \quad {r0_z}]" + r"\text{ km}")
        st.latex(r"\text{Initial Velocity Vector: }" + fr"[{v0_x} \quad {v0_y} \quad {v0_z}]" + r"\text{ km/s}")
        st.latex(r"\text{Simulation Time: }" + fr"{tf_val:.2f} " + fr" \text{{ {tf_unit}}}")
        st.latex(r"\text{Maneuver Time: }" + fr"{t_maneuver:.2f} " + fr" \text{{ {t_maneuver_unit}}}")
        st.latex(r"\text{Maneuver Velocity Change (Δv): }" + fr"[{del_v_x} \quad {del_v_y} \quad {del_v_z}]" + r"\text{ km/s}")

    oe_i = vector2OE(orbit_data[0], orbit_data[1])
    oe_f = vector2OE(orbit_data[2], orbit_data[3])

    df = pd.DataFrame({
            "Orbital Elements": ["Semi Major Axis", "Eccentricity", "Inclination", "RAAN", "Argument of Perigee", "True Anomaly at Epoch"],
            "Initial Value": oe_i,
            "Final Value": oe_f})
    st.table(df)
