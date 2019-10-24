import numpy as np
import bitmaps as bmp
import time
import pylaunchpad as pylp


def rotate_bitmap(bmp, amount=1):
    """
    Quick and dirty rotate an 8*8 bitmap 90 degrees clockwise
    :param bmp:
    :return:
    """
    bit_length = 8
    bin_bitmap = []
    # First build a bitmap from the 8 decimal numbers
    for row in bmp:
        bits = []
        bin_val = bin(row)[2:].zfill(bit_length)
        for bit in range(bit_length):
            bits.append(bin_val[bit])
        bin_bitmap.append(bits)
    # Rotate the bitmap
    bin_rot = np.rot90(bin_bitmap,amount,axes=(1,0))
    rotated_bmp = []
    # convert the bitmap back to a list of decimal numbers
    for row in bin_rot:
        dec_val = sum(int(b) << i for i, b in enumerate(row[::-1]))
        rotated_bmp.append(dec_val)
    return rotated_bmp

def spin_ghost():
    pad = pylp.get_me_a_pad()
    ghost = bmp.ghost_one
    colours = ['red', 'green', 'blue', 'yellow','red']
    for spin in range(5):
        pad.draw_colour = pad.colours[colours[spin]]
        pad.draw_char(ghost)
        time.sleep(0.5)
        ghost = rotate_bitmap(ghost)

spin_ghost()