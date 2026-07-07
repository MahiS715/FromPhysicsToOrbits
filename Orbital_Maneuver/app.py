from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
ROOT_common = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT_common))

import streamlit as st
import numpy as np
import plotly.graph_objects as go