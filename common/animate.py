# Animation Button Options
play_opt = dict(frame=dict(duration=33, redraw=True),
                            transition=dict(duration=0),
                            fromcurrent=True)
pause_opt = dict(frame=dict(duration=0, redraw=True),
                            mode="immediate",
                            transition=dict(duration=0))
reset_opt = dict(frame=dict(duration=0, redraw=True),
                            mode="immediate",
                            transition=dict(duration=0))

# Buttons
play_button = dict(label="    Play    ", method="animate", args=[None, play_opt])
pause_button = dict(label="   Pause   ", method="animate", args=[[None], pause_opt])
reset_button = dict(label="   Reset   ", method="animate", args=[["0"], reset_opt])