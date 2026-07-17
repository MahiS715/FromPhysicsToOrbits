import streamlit as st

st.image("images/orbit-nasa-hubble-space-telescope-cropped.jpg", caption='Photo by NASA Hubble Space Telescope on Unsplash')
st.success("You can choose Applications to Explore in the Top Left Corner")

pages = {
    "Applications": [
        st.Page("2D_Orbit_Propagation/app_2Dop.py", title="2D Orbit Propagator"),
        st.Page("3D_Orbit_Visualisation/app_3Dov.py", title="3D Orbit Visualiser"),
        st.Page("Orbital_Maneuver/app_om.py", title="Orbital Maneuver")
    ]
}

pg = st.navigation(pages, position="top")
pg.run()
