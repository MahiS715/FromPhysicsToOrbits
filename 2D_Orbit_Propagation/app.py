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


from common.constants import MU_EARTH, RE
from common.orbit import orbit_2d

if "simulation_done" not in st.session_state:
    st.session_state.simulation_status = False

if "orbit_data" not in st.session_state:
    st.session_state.orbit_data = None

st.title("2D Orbit Propagator")

tab_plot, tab_animation = st.tabs(["Plot", "Animation"])

with tab_plot:
    st.info("Enter the Initial Radius and Velocity Vector to Find your Satellite's Orbit around Earth")

    st.write("")

    conversion_to_seconds = {"sec": 1,
                            "min": 60,
                            "hr": 60*60,
                            "day": 24*60*60,
                            "yr": 365.25*24*60*60}

    with st.form("Propagation_Input"):
        colr, colv, colt = st.columns([2, 2, 3])
        with colr:
            st.latex(r"\text{Radius Vector}")
            r0_x = st.number_input("X Component (km)", value=7000.0, step=100.0)
            r0_y = st.number_input("Y Component (km)", value=0.0, step=100.0)

        with colv:
            st.latex(r"\text{Velocity Vector}")
            v0_x = st.number_input("X Component (km/s)", value=0.0000, step=0.1, format="%.4f")
            v0_y = st.number_input("Y Component (km/s)", value=7.5000, step=0.1, format="%.4f")

        with colt:
            st.latex(r"\text{Simulation Parameters}")
            colt1, colt2 = st.columns([3, 2])
            with colt1:
                tf_val = st.number_input("Simulation Time", min_value=1.0, value=1.0, step=1.0)
                tf_step = st.number_input("Simulation Output Step", min_value=1, value=1, step=1)

            with colt2:
                tf_unit = st.selectbox("Time Unit", ["sec", "min", "hr", "day", "yr"], index=3)
                tf_unit_step = st.selectbox("Time Unit (Step)", ["sec", "min", "hr", "day", "yr"], index=0)
            
            tf = tf_val*conversion_to_seconds[tf_unit]
            tf_unit_step_sec = tf_step*conversion_to_seconds[tf_unit_step]

            req_points = max(1000, int(tf/tf_unit_step_sec))
            num_points = min(50000, req_points)
            teval = np.linspace(0, tf, num_points)

        propagate = st.form_submit_button(label="Propagate", help="Click to Propagate your Orbit")


    if propagate:
        colpt1, colpt2 = st.columns([7, 3])
        with colpt1:
            st.info("The step size will be defaulted to Points in the range(1000, 50000)")
        with colpt2:
            st.success(f"No of Points used: {num_points}")

        r0 = np.array([r0_x, r0_y])*1e3
        v0 = np.array([v0_x, v0_y])*1e3


        with st.spinner("Solving the Orbit...", show_time=True):
            start = time.perf_counter()
            sol = solve_ivp(orbit_2d, t_span=[0, tf], y0=np.concatenate((r0, v0)), t_eval=teval,
                            method="DOP853", dense_output=False,
                            rtol=1e-10, atol=1e-12)
            elapsed = time.perf_counter() - start
            st.session_state.orbit_data = sol
            st.session_state.simulation_status = True

        st.metric("Propagation Time", f"{elapsed:.3f} s")


        fig = go.Figure()
        fig.add_shape(type="circle", xref='x', yref='y', x0=-RE, y0=-RE , x1=RE , y1=RE,
                    line_color="#007BFF", fillcolor="#007BFF")
        fig.add_trace(go.Scattergl(x=sol.y[0], y=sol.y[1],
                                mode='markers', name='Orbit', marker=dict(size=1, color='white')))
        fig.update_traces(hoverinfo="skip")
        fig.update_xaxes(visible=False)
        fig.update_yaxes(scaleanchor='x', scaleratio=1, visible=False)
        st.plotly_chart(fig)

        st.info("Please use Full Screen to Visualise Propagated Orbit | Double Click to Reset View")

with tab_animation:

    if not st.session_state.simulation_status:
        st.warning("Propagate the Orbit in Tab 1 First")
        st.stop()

    sol_anim = st.session_state.orbit_data

    st.info("Hit Play, Pause & Reset to View Animated Orbit | Hover over to View the Coordinates")

    with st.spinner("Animating the Orbit...", show_time=True):
        fig_animation = go.Figure(data=[go.Scatter(x=[sol_anim.y[0, 0]], y=[sol_anim.y[1, 0]], mode="markers", marker=dict(size=1, color='white'))])
        fig_animation.add_shape(type="circle", xref='x', yref='y', x0=-RE, y0=-RE , x1=RE , y1=RE,
                        line_color="#007BFF", fillcolor="#007BFF")
        frames = [go.Frame(data=[go.Scatter(x=[sol_anim.y[0, i]], y=[sol_anim.y[1, i]], mode="markers", marker=dict(size=1, color="white"))], name=str(i))
                for i in range(0, num_points, 20)]
        fig_animation.frames = frames

        play_animate_options = dict(frame=dict(duration=33, redraw=False),
                                    transition=dict(duration=0),
                                    fromcurrent=True)
        pause_animate_options = dict(frame=dict(duration=0, redraw=False),
                                    mode="immediate",
                                    transition=dict(duration=0))
        reset_animate_options = dict(frame=dict(duration=0, redraw=True),
                                    mode="immediate",
                                    transition=dict(duration=0))
        play_button = dict(label="    Play    ", method="animate", args=[None, play_animate_options])
        pause_button = dict(label="   Pause   ", method="animate", args=[[None], pause_animate_options])
        reset_button = dict(label="   Reset   ", method="animate", args=[["0"], reset_animate_options])

        fig_animation.update_layout(xaxis=dict(range=[1.5*min(sol_anim.y[0]), 1.5*max(sol_anim.y[0])]),
                                    yaxis=dict(range=[1.5*min(sol_anim.y[1]), 1.5*max(sol_anim.y[1])]),
                                    updatemenus=[dict(type="buttons", showactive=False, 
                                                    direction="left", x=0.5, xanchor="center", y=-0.1, yanchor="top", 
                                                    buttons=[play_button, pause_button, reset_button])])
        fig_animation.update_xaxes(visible=False)
        fig_animation.update_yaxes(scaleanchor='x', scaleratio=1, visible=False)
        config = dict(displayModeBar=False)   
    st.plotly_chart(fig_animation, config=config)
