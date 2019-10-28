"""
This is where we will be typing our code for the workshop
"""

import pylaunchpad as lp
import time
import snow_tree as tree
pad = lp.get_me_a_pad()
pad.reset()

pad.setup_painter_colours()
pad.in_ports.set_callback(pad.paint_app)
while True:
    if pad.last_x >= pad.max_x and pad.last_y == 8:
        break
    time.sleep(.4)
pad.in_ports.cancel_callback()
lp.save_frame(pad.painter_frame)
