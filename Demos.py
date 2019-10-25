"""
Demos for the Python Launchpad library
"""
import os
import time
from random import choice
from random import randint

import bitmaps as bmp
import narrow_letters as nl
import pylaunchpad as pylp
import show_patterns as patterns
import wide_font as wf


def ghost(pad):
    """
    Draw a set of Pacman style ghosts
    :param pad: A launchpad class object
    :return:
    """
    pad.draw_char(bmp.ghost_one)
    time.sleep(1)
    pad.draw_char(bmp.ghost_two)
    time.sleep(1)
    pad.draw_colour = pad.colours['red']
    pad.draw_char(bmp.ghost_three)
    time.sleep(1)
    pad.draw_char(bmp.ghost_four)


def heart(pad):
    """
    Display a flashing heart
    :param pad:
    :return:
    """
    for _ in range(4):
        pad.draw_char(bmp.heart_1)
        time.sleep(0.5)
        pad.draw_char(bmp.heart_1f)
        time.sleep(0.5)

    for _ in range(4):
        pad.draw_char(bmp.heart_2)
        time.sleep(0.5)
        pad.draw_char(bmp.heart_2f)
        time.sleep(0.5)


def show_alphabet(pad, wide=False):
    """
    Show all the ASCII characters from 65-123
    :param pad:
    :param bool wide: Use the Wider font
    :return:
    """
    for i in range(65, 123):
        try:
            if wide:
                char_data = wf.letters[chr(i)]
            else:
                char_data = nl.letters[chr(i)]
            # print(char_data)
            pad.draw_char(char_data)
            time.sleep(.1)
        except KeyError:
            # Just in case we don't have that character, just pass
            pass


def quick_test(pad):
    """
    A quick chaser to turn all the leds on and off one at a time
    :return:
    """
    for y in range(9):
        for x in range(9):
            if x > 0:
                pad.set_led_xy_by_colour(x - 1, y, pad.colours['off'])
            pad.set_led_xy_by_colour(x, y, pad.colours['red'])
            time.sleep(.1)
            if x == 8:
                pad.set_led_xy_by_colour(x, y, pad.colours['off'])


def countdown(pad, start=9):
    """
    Count down from start to 0, with a 1 second gap
    :param pad:
    :param start:
    :return:
    """
    if start > 9:
        start = 9
    pad.draw_colour = pad.colours['green']
    for i in range(start, -1, -1):
        if 6 > i > 3:
            pad.draw_colour = pad.colours['orange']
        char = str(i)
        char_data = nl.letters[char]
        pad.draw_char(char_data, 2)
        time.sleep(1)

        if i < 4:
            pad.draw_colour = pad.colours['red']


def show_colour(pad):
    for i in range(255):
        pad.draw_colour = i
        pad.draw_char(nl.letters['J'])
        print(i)
        os.system('pause')


def show_colours(pad):
    for red in range(4):
        for green in range(4):
            colour = green << 4 | red
            print(f"Colour = {colour}, red = {red}, green = {green}")
            pad.draw_colour = colour
            pad.draw_char(nl.letters['J'])
            os.system('pause')


def scan_for_buttons(pad, duration=10):
    """
    Report which buttons are being pressed for the total duration
    :param pad:
    :param duration:
    :return:
    """
    t_end = time.time() + duration
    while time.time() < t_end:
        pad.button_state_xy()


def fade_up(pad, char):
    for i in range(4):
        pad.draw_colour = i | i << 4
        pad.draw_char(char)
        time.sleep(.03)


def fade_down(pad, char):
    previous_colour = pad.draw_colour
    for i in range(4):
        pad.draw_colour = (3 - i) | (3 - i) << 4
        pad.draw_char(char)
        time.sleep(.03)
    pad.draw_colour = previous_colour


def show_x_y_coordinates(pad):
    """
    Display the X/Y coordinate of the any pressed button for a total of 10 seconds
    The top row will be used as a countdown indicator
    :param pad:
    :return:
    """
    for i in range(0, 8):
        pad.set_led_xy(i, 0, 53, 53, 53)
        time.sleep(.1)
    print("setting the callback function for 8 secs")
    pad.in_ports.set_callback(pad.midi_in_cb)
    for i in range(8):
        time.sleep(1)
        # Turn off the very top row lights to indicate how much time remains using the call back feature
        pad.set_led_xy(8 - i, 0, 0, 0, 0)
    print("Cancelling the callback function")
    pad.in_ports.cancel_callback()
    time.sleep(.5)
    pad.reset()


def show_message(pad):
    start_delay_time = pad.delay_time
    pad.delay_time = .05
    msg = "Hi!"
    pad.scroll_up(msg)
    msg = "Hi"
    pad.scroll_message(msg, pad.SCROLL_RIGHT)
    msg = "Hi Joe"
    pad.scroll_message(msg, pad.SCROLL_LEFT)
    pad.delay_time = start_delay_time


def green_ghost(pad):
    pad.draw_colour = pad.colours['green']
    pad.clear_frame_buffer()
    pad.scroll_on_left(bmp.ghost_three)
    time.sleep(.2)
    pad.draw_char(bmp.ghost_one)
    time.sleep(.2)
    pad.scroll_on_right(nl.letters[' '])


def ghost_left_right(pad):
    pad.scroll_on_left(bmp.ghost_one)
    pad.scroll_on_left(nl.letters[' '])
    pad.scroll_on_right(bmp.ghost_one)
    pad.scroll_on_right(nl.letters[' '])


six = "90009", "00000", "90009", "00000", "90009"
five = "90009", "00000", "00900", "00000", "90009"
four = "90009", "00000", "00000", "00000", "90009"
three = "90000", "00000", "00900", "00000", "00009"
two = "00000", "00900", "00000", "00900", "00000"
one = "00000", "00000", "00900", "00000", "00000"
dice = [one, two, three, four, five, six]


def random_dice(lp):
    prev_roll = 0
    for _ in range(0, randint(20, 50)):
        roll = randint(1, 6)
        while roll == prev_roll:
            roll = randint(1, 6)
        roll_dice(lp, roll)
        prev_roll = roll
        time.sleep(0.05)


def roll_dice(lp, value):
    bitmap = dice[value - 1]
    print(f"Rolling {value}")

    for y in range(0, 5):
        for x in range(0, 5):
            bright = int(bitmap[y][x]) * 5
            if bright == 0:
                lp.set_led_xy_by_colour(x, y + 1, lp.colours["black"])
            else:
                lp.set_led_xy_by_colour(x, y + 1, lp.colours["white"])


def tree(pad):
    """
    Draw a christmas tree
    :param pad:
    :return:
    """
    pad.draw_colour = pad.colours['green']
    pad.draw_char(bmp.tree)


def snow(pad):
    """
    Animate falling snow on the tree bitmap, redrawing any green pixels as the snow falls down
    :param pad:
    :return:
    """
    # A bitmap of possible snow flake positions, that are added to a list and plotted for each row
    # This lets us identify if a tree pixel gets overwritten with snow and re draw it once the snow has fallen
    snow_flakes = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x00, 0x40, 0x00, 0x80, 0x00]

    snow_rows = []
    for _ in range(10):
        snow_rows.insert(0, choice(snow_flakes))

        for y in range(len(snow_rows)):
            draw_single_snow_row(pad, snow_rows, y)
        if len(snow_rows) == 9:
            snow_rows.pop(8)
        time.sleep(.8)


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


def get_tree_row_data(y):
    if y == 0:
        tree_row = 0
    else:
        tree_row = bmp.tree[y - 1]
    return tree_row


def demos(pad):
    pad.reset()
    countdown(launchpad)
    for _ in range(5):
        fade_up(pad, bmp.invader_two)
        fade_down(pad, bmp.invader_two)

    pad.draw_colour = pad.colours['red']
    time.sleep(1)
    pad.delay_time = 0.1
    pad.scroll_frames_right([bmp.invader_one, bmp.invader_two])
    pad.scroll_frames_right([bmp.pac_one, bmp.pac_two])

    show_message(pad)
    print("Press a pad to see its X & Y coordinates")
    show_x_y_coordinates(launchpad)

    green_ghost(pad)
    # launchpad.scroll_data_left( ghost_one, nl.letters[' '])
    # time.sleep(0.5)
    # launchpad.scroll_data_right(nl.letters[' '], ghost_one)
    # launchpad.scroll_data_right( ghost_one, nl.letters[' '])
    # time.sleep(1)

    show_alphabet(pad)
    ghost(pad)
    time.sleep(1)
    pad.reset()


def fat_font():
    msg = "Testing 1 ABC"
    for c in msg:
        launchpad.draw_char(nl.letters[c])
        time.sleep(.6)
        launchpad.draw_char(wf.letters[c])
        time.sleep(.6)


def painter(pad):
    """
    Light the pressed pad with a random colour
    :param pad:
    :return:
    """
    pad.reset()
    pad.last_y = 0
    pad.last_x = 0
    pad.in_ports.set_callback(pad.painter_cb)
    while True:
        if (pad.last_x == 8) and (pad.last_y == 8):
            break
        time.sleep(.4)
    pad.in_ports.cancel_callback()
    pad.reset()


def painter_with_colour(pad):
    """
    A slightly more advanced painter routine
    :param pad:
    :return:
    """
    # set the top row to a set of colours
    pad.reset()
    for x, colour in enumerate(pad.painter_colours):
        r, g, b = colour
        pad.set_led_xy(x, 0, r, g, b)
    pad.last_y = 0
    pad.last_x = 0
    pad.red, pad.green, pad.blue = pad.painter_colours[0]
    pad.in_ports.set_callback(pad.painter_cb_colour)
    while True:
        if pad.last_x == 8 and pad.last_y == 8:
            break
        time.sleep(.4)
    pad.in_ports.cancel_callback()

    pad.reset()


launchpad = pylp.get_me_a_pad()

# launchpad.scroll_frames_right([source_bmp.pac_one, source_bmp.pac_two])
painter_with_colour(launchpad)

demos(launchpad)
print("Press any of the Launchpad Keys or the bottom right pad to exit")
painter(launchpad)
print("Choose a colour to paint with or the bottom right pad to exit")
painter_with_colour(launchpad)

patterns.show_file(launchpad, "fireworks.csv")
random_dice(launchpad)
heart(launchpad)
launchpad.reset()
# scan_for_buttons(launchpad,4990)

tree(launchpad)
snow(launchpad)
launchpad.reset()

# https://xantorohara.github.io/led-matrix-editor/#
