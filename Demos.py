"""
Demos for the Python Launchpad library
"""
import os
import sys
import time

import bitmaps as bmp
import narrow_letters as nl
import wide_font as wf
import pylaunchpad as pylp
from random import choice
from random import randint
import show_patterns as patterns

import csv


def ghost(pad):
    """
    Draw a ghost
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
    for loop in range(6):
        pad.draw_char(bmp.heart_1)
        time.sleep(0.5)
        pad.draw_char(bmp.heart_1f)
        time.sleep(0.5)

    for loop in range(6):
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
            print(char_data)
            pad.draw_char(char_data)
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
            print("Colour = {}, red = {}, green = {}".format(colour, red, green))
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
        pad.set_led_xy(i, 0, 3, 3, 3)
        time.sleep(.1)
    print("setting the callback function for 8 secs")
    pad.in_ports.set_callback(pad.midi_in_cb)
    for i in range(36):
        time.sleep(1)
        # Turn off the very top row lights to indicate how much time remains using the call back feature
        pad.set_led_xy(8 - i, 0, 0, 0, 0)
    print("Cancelling the callback function")
    pad.in_ports.cancel_callback()
    time.sleep(.5)
    pad.reset()


def show_message(pad):
    msg = "Hi!"
    time.sleep(.1)
    pad.scroll_up(msg)

    time.sleep(1)
    msg = "Hi"
    pad.scroll_message(msg, pad.SCROLL_RIGHT)
    time.sleep(1)
    msg = "Hi Joe"
    pad.scroll_message(msg, pad.SCROLL_LEFT)


def green_ghost(pad):
    pad.draw_colour = pad.colours['green']
    pad.clear_frame_buffer()
    pad.scroll_on_left(bmp.ghost_three)
    time.sleep(.2)
    pad.draw_char(bmp.ghost_one)
    time.sleep(.2)
    pad.scroll_on_right(nl.letters[' '])


def ghost_left_rignt(pad):
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


def randomdice(lp):
    prevroll = 0
    for _ in range(0, randint(20, 50)):
        roll = randint(1, 6)
        while roll == prevroll:
            roll = randint(1, 6)
        rolldice(lp, roll)
        prevroll = roll
        time.sleep(0.05)


def rolldice(lp, value):
    bitmap = dice[value - 1]
    #    print (bitmap)
    #    print()

    print("Rolling " + str(value))

    for y in range(0, 5):
        for x in range(0, 5):
            bright = int(bitmap[y][x]) * 5
            if bright == 0:
                lp.set_led_xy_by_colour(x, y + 1, lp.colours["black"])

            else:
                lp.set_led_xy_by_colour(x, y + 1, lp.colours["white"])


def get_me_a_pad():
    # Create a LaunchPad midi object to help us find the midi port a launchpad is connected to
    lp_midi = pylp.LPMidi()
    # Firstly find the port we can send messages to the Launchpad
    out_port = lp_midi.find_launchpad_out_port()
    # Now the port we will receive messages from
    in_port = lp_midi.find_launchpad_in_port()
    if out_port is not None:
        print("Midi out {}, name {}".format(out_port, lp_midi.name))
        if in_port is not None:
            print("Midi in {}, name {}".format(in_port, lp_midi.name))

    else:
        print("No Launchpad detected")
        sys.exit()
    # This code supports LaunchPad mini or Launchpad Mk2
    # TODO need am LpMiniMk3
    if "MiniMK3" in lp_midi.name:
        pad = pylp.LaunchpadMiniMk3(lp_midi.name, out_port, in_port)

    elif "Mini" in lp_midi.name:
        pad = pylp.LpMini(lp_midi.name, out_port, in_port)
    else:
        pad = pylp.LaunchpadMk2(lp_midi.name, out_port, in_port)
    pad.draw_colour = pad.colours['red']
    # Connect up and reset the LaunchPad
    pad.open()

    pad.programmer_mode()
    pad.reset()
    return pad


def tree(pad):
    pad.draw_colour = pad.colours['green']
    pad.draw_char(bmp.tree)


def snow(pad):
    snow = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x00, 0x40, 0x00, 0x80, 0x00]

    snow_rows = []
    while True:
        snow_rows.insert(0, choice(snow))

        for y in range(len(snow_rows)):
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
        if len(snow_rows) == 9:
            snow_rows.pop(8)
        time.sleep(1)


def get_tree_row_data(y):
    if y == 0:
        tree_row = 0
    else:
        tree_row = bmp.tree[y - 1]
    return tree_row


def snow_two(pad):
    # choose an random x,y (0-8, 1-8
    # choose draw not draw
    # if draw, then set pixel, x,y white
    # if not draw , then AND with bit x, y of tree
    # create a queue of snow co-ords, every other op, set them back
    prev_x = 0
    prev_y = 0
    for i in range(255):
        x = randint(0, 8)
        y = randint(1, 8)
        draw_snow = randint(0, 10)
        mask = 128 >> x
        tree_row = bmp.tree[y - 1]
        if draw_snow > 3:
            pad.set_led_xy_by_colour(x, y, pad.colours['white'])
            prev_x = x
            prev_y = y
        else:
            if tree_row & mask:
                pad.set_led_xy_by_colour(x, y, pad.colours['green'])
                if prev_y > 0:
                    pad.set_led_xy_by_colour(prev_x, prev_y, pad.colours['green'])
            else:
                if prev_y > 0:
                    pad.set_led_xy_by_colour(prev_x, prev_y, pad.colours['green'])
                pad.set_led_xy_by_colour(x, y, pad.colours['black'])


def animate(pad):
    #with open ("./patterns/fireworks.csv") as converted:
    with open("C:\\Users\\Joe.deller\\Downloads\\matrixbitmaps\\MatrixBitmaps\\fireworks.csv") as converted:
        data = csv.reader(converted)
        frames = list(data)
        frame_count = int(len(frames) / 8)

        print(f"I read {frame_count}")
    for frame in range(frame_count):
        for y in range(8):
            row_data = frames[frame * 8 + (y * 8)]
            for bit in row_data:
                bit = int(bit)
                red = int(bit) >> 16
                green = int(bit) >> 8
                blue = int(bit) & 255
                pad.set_led_xy(bit, y, red, green, blue)


def demos(pad):
    pad.reset()
    # countdown(pad)
    # Set the drawing colour to red

    # Scroll a space invader character from left to right, switching between the two frames
    # of animation

    for _ in range(5):
        fade_up(pad, bmp.invader_two)
        fade_down(pad, bmp.invader_two)

    pad.draw_colour = pad.colours['red']
    time.sleep(1)
    pad.delay_time = 0.1
    pad.scroll_frames_right([bmp.invader_one, bmp.invader_two])
    pad.scroll_frames_right([bmp.pac_one, bmp.pac_two])

    show_message(pad)
    # show_x_y_coordinates(pad)
    # quick_test()
    # pad.draw_char(nl.letters['A'])
    # time.sleep(1)
    # scan_for_buttons(pad, duration=10)
    # show_colour()
    # countdown()
    # countdown(pad)
    green_ghost(pad)
    # pad.scroll_data_left( ghost_one, nl.letters[' '])
    # time.sleep(0.5)
    # pad.scroll_data_right(nl.letters[' '], ghost_one)
    # pad.scroll_data_right( ghost_one, nl.letters[' '])
    # time.sleep(1)

    show_alphabet(pad)
    ghost(pad)
    # pad.reset()


def set_wash(r, g, b):
    for x in range(9):
        for y in range(9):
            pad.set_led_xy(x, y, r, g, b)


def set_wash_single(colour):
    for x in range(9):
        for y in range(9):
            pad.set_led_xy_by_colour(x, y, colour)


def gui():
    layout = [[SG.Text('Adjust the sliders for Red, Green & Blue levels.')],

              [SG.Slider(range=(0, 63), orientation='v', size=(12, 20), default_value=0),
               SG.Slider(range=(0, 63), orientation='v', size=(12, 20), default_value=0),
               SG.Slider(range=(0, 63), orientation='v', size=(12, 20), default_value=0)],
              [SG.Button('Ok'), SG.Button('Cancel')]
              ]

    # Create the Window
    window = SG.Window('Launchpad Colour Mixer', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    red, green, blue = 0, 0, 0
    while True:
        update = False
        event, values = window.read(timeout=50)
        new_red, new_green, new_blue = values[0], values[1], values[2]
        if new_red != red:
            red = new_red
            update = True
        if new_blue != blue:
            blue = new_blue
            update = True
        if new_green != green:
            green = new_green
            update = True
        if update:
            print(f"Red {values[0]}, Green {values[1]}, Blue {values[2]}")
            set_wash(values[0], values[1], values[2])
            # set_wash_single(values[0])
        if event in (None, 'Cancel'):  # if user closes window or clicks cancel
            break
    print(values)

    window.close()
    pad.reset()

def fat_font():
    msg = "Testing 1 ABC"
    for c in msg:
        pad.draw_char(nl.letters[c])
        time.sleep(.6)
        pad.draw_char(wf.letters[c])
        time.sleep(.6)



def painter(pad):
    pad.in_ports.set_callback(pad.painter_cb)
    for i in range(40):
        # print("setting the callback function for 8 secs")
        time.sleep(.4)
    pad.in_ports.cancel_callback()


# painter()



pad = get_me_a_pad()
#snow(pad)
#demos(pad)

# show_x_y_coordinates(pad)

#pad.scroll_message("Hi Joe")
# fat_font()
# pad.led_all_on()

# pad.set_all_on(32,32,32)
time.sleep(1)
## patterns.show_all(pad)
#patterns.show_file(pad, "fireworks.csv")
# pad.draw_char(bmp.club)
# randomdice(pad)
# heart(pad)
# for x in range(11,20):
#    pad.set_led_by_number(x,44)
import PySimpleGUI as SG

gui()

#scan_for_buttons(pad,4990)
pad.draw_char(nl.letters['A'])

tree(pad)

snow(pad)
demos(pad)
# animate(pad)
# https://xantorohara.github.io/led-matrix-editor/#
