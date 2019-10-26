"""
This is where we will be typing our code for the workshop
"""
import pylaunchpad as pylp
import time

pad = pylp.get_me_a_pad()
pad.setup_painter_colours()
pad.in_ports.set_callback(pad.paint_app)
while True:
    if pad.last_x >= 8 and pad.last_y == 8:
        break
    time.sleep(.4)
pad.in_ports.cancel_callback()
pylp.save_frame(pad.painter_frame)

