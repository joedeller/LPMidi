"""
Based on Lady Ada's Arduino code for RGB 8*8 LED Matrices
Launchpads only have 0-63 values for colour (TODO , 0-63, not 0-127)
"""
import pylaunchpad as lp
import time


def wheel(wheel_pos):
    """
    Input a value 0 to 127 to get a color value.
    The colours are a transition r - g - b - back to r.
    :param wheel_pos:
    :return:
    """
    # TODO - Launchpads only support 0-63, far fewer values than a 8*8 RGB panel
    wheel_pos = 127 - wheel_pos
    if wheel_pos < 42:  # was 85
        return 127 - wheel_pos * 3, 0, wheel_pos * 3

    if wheel_pos < 85:
        wheel_pos -= 42
        return 0, wheel_pos * 3, 127 - wheel_pos * 3

    wheel_pos -= 85
    return wheel_pos * 3, 127 - wheel_pos * 3, 0


def theatre_chase(pad, r, g, b, step=5):
    """

    :param pad: A launchpad Object from get_me_a_pad()
    :param int r: Red level (0-63)
    :param int g: Green level
    :param int b:Blue level
    :param step: How far apart the chaser columns are
    :return:
    """
    for _ in range(0, 32):
        for col in range(0, step):
            for y in range(0, 9):
                for x in range(0, 8, step):
                    pad.set_led_xy(x + col, y, r, g, b)
            time.sleep(.09)
            for y in range(0, 9):
                for x in range(0, 8, step):
                    pad.set_led_xy(x + col, y, 0, 0, 0)


def theater_chase_rainbow(pad):
    step = 5
    for j in range(0, 64):
        for column in range(0, step):
            for y in range(0, 9):
                for x in range(0, 8, step):
                    r, g, b = (wheel((x + (y * 9) + j) % 127))
                    pad.set_led_xy(x + column, y, r, g, b)
            time.sleep(.09)
            for y in range(0, 9):
                for x in range(0, 8, step):
                    pad.set_led_xy(x + column, y, 0, 0, 0)


# Slightly different, this makes the rainbow equally distributed throughout


def rainbow_cycle(pad):
    """
    Light the whole pad with a changing rainbow colour cycle
    :param pad:
    :return:
    """
    for j in range(0, 128 * 2):  # // 2 cycles of all colors on wheel
        for i in range(0, 80):
            f = i * 128.0 / 80.0

            x = i % 9
            y = int(i / 9)
            r, g, b = (wheel(((int(f)) + j) & 127))
            pad.set_led_xy(x, y, r, g, b)


def rainbow_pad(pad):
    """
    Cycle a range of rainbow colours from bottom right to top left
    :param pad:
    :return:
    """
    for j in range(0, 128 * 2):  # // 2 cycles of all colors on wheel
        for y in range(0, 9):
            r, g, b = (wheel((y + j) & 127))
            for x in range(0, 9):
                pad.set_led_xy(x, y, r, g, b)


launchpad = lp.get_me_a_pad()

# rainbow_pad(launchpad)
# rainbow_cycle(launchpad)
# theatre_chase(launchpad, 40, 50, 10, step=3)
theater_chase_rainbow(launchpad)
