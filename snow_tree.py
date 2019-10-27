import pylaunchpad as lp
import bitmaps as bmp
import time
from random import choice


def get_tree_row_data(y):
    if y == 0:
        tree_row = 0
    else:
        tree_row = bmp.tree[y - 1]
    return tree_row


def draw_single_snow_row(pad, snow_rows, y):
    for x in range(0, 8):
        # the tree starts at row 1, so for row 0, snow is always drawn
        mask = 128 >> x
        tree_row = get_tree_row_data(y)

        if mask & snow_rows[y]:
            pad.set_led_xy_by_colour(x, y, pad.colours['white'])
        else:
            if tree_row & mask:
                pad.set_led_xy_by_colour(x, y, pad.colours['green'])
            else:
                pad.set_led_xy_by_colour(x, y, pad.colours['black'])


def tree(pad):
    """
    Draw a christmas tree
    :param pad:
    :return:
    """
    pad.draw_colour = pad.colours['green']
    pad.draw_char(bmp.tree)


def snow_tree(pad):
    snow_flakes = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x00, 0x40, 0x00, 0x80, 0x00]

    snow_rows = []
    for _ in range(10):
        snow_rows.insert(0, choice(snow_flakes))

        for y in range(len(snow_rows)):
            draw_single_snow_row(pad, snow_rows, y)
        if len(snow_rows) == 9:
            snow_rows.pop(8)
        time.sleep(.8)


if __name__ == "__main__":
    launchpad = lp.get_me_a_pad()
    launchpad.reset()
    tree(launchpad)
    snow_tree(launchpad)
