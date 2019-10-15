"""
Inspired by Blinkinlabs pattern paint tool, which saves data in a 565 RGB format, which was then converted
for use with the Launchpad
https://blinkinlabs.com/blinkytape/patternpaint/
"""
import os
import time
from random import randint
import glob


def get_csvfiles(directory):
    return [f for f in glob.glob(directory + "\\patterns\\*.csv")]


def frame_count(filename):
    """
    Simple count the number of lines in a file.  For small files this isn't worth optimising
    For files that are hundreds of K then a different approach might be needed
    For now it's plenty fast enough
    Not there is no exception handling at all
    :param filename: The file we want to count the number of lines in
    :return: The number of lines
    """
    return len(open(filename).readlines())


def read_file(my_file):
    """
    Open a CSV file that was created by the convert 565 tool.
    The format will be rows of 8 RGB 24 bit values
    Every 8 rows is considered to be a single frame of animation
    There should be at least 8 rows and only multiples of 8
    The code does not validate the file in any way
    The data is read into a list of frames, which are then appended to a master list of frames
    :return: A list of lists, each entry has 64 byte_count of RGB data for the 8*8 Matrix
    """

    total_frames = int(frame_count(my_file))
    mem_frames = []
    with open(my_file) as f:
        for frame in range(total_frames):
            frame_mem = []
            data = f.readline().split(",")
            for y in range(8):
                for x in range(8):
                    packed = int(data[y * 8 + x])
                    frame_mem.append(packed)
            mem_frames.append(frame_mem)

    return mem_frames


def show_frames(pad, frame_data, modify_colour=False):
    """
    Show a series of frames on the Launchpad
    :param pad: A launchpad object
    :param frame_data:The list of frames we want to display
    :param modify_colour: If we want random colours, set to true
    :return:
    """
    # TODO - Use the faster sysex method of single message with all the rgb data
    for frame in range(len(frame_data)):
        if modify_colour:
            red = randint(0, 63)
            green = randint(0, 63)
            blue = randint(0, 63)

        current_frame = frame_data[frame]
        time.sleep(0.05)
        for y in range(8):
            for x in range(8):
                packed = current_frame[y * 8 + x]
                if packed > 0 and modify_colour:  # if the colour is not black
                    pad.set_led_xy(x, y, red, green, blue)
                else:
                    # Unpack the RGB value into its separate Red, Green & Blue values
                    r = (packed & 0xFF0000) >> 16  # Shift the red value into the right most 8 bits
                    g = (packed & 0xFF00) >> 8  # Shift the green value into the right most 8 bits
                    b = packed & 0xFF  # Mask off the top two byte_count containing the red & green

                    pad.set_led_xy(x, y + 1, int(r), int(g), int(b))


def show_single_frame(pad, single_frame):
    """
    Show a single frame from the animation CSV file,
    which contains a series of 24bit pixels
    :param pad:
    :param single_frame:
    :return:
    """
    for y in range(8):
        for x in range(8):
            packed = single_frame[y * 8 + x]
            r = (packed & 0xFF0000) >> 16
            g = (packed & 0xFF00) >> 8
            b = packed & 0xFF
            pad.set_led_xy(x, y, int(r), int(g), int(b))


def show_all(pad):
    pad.reset()
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file_list = get_csvfiles(current_dir)
    for file in file_list:
        show_file(pad, file, append_path=False)


def show_file(pad, filename, append_path=True):
    if append_path:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        filename = f"{current_dir}\\patterns\\{filename}"
    print(f"Using file {filename}")

    frame_data = read_file(filename)
    frames = len(frame_data)
    print(f"frame_data has {frames} frames")
    show_frames(pad, frame_data)
    for i in range(2):
        # show_frames(pad, frame_data, True)
        # time.sleep(0.1)
        show_frames(pad, frame_data, False)
        # time.sleep(0.1)
