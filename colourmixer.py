import PySimpleGUI as PyGui
import pylaunchpad as pylp


def set_wash(pad, r, g, b):
    for x in range(9):
        for y in range(9):
            pad.set_led_xy(x, y, r, g, b)


def set_wash_fast(pad, r, g, b):
    pad.set_all_on(r, g, b)


def set_wash_single(pad, colour):
    for x in range(9):
        for y in range(9):
            pad.set_led_xy_by_colour(x, y, colour)


def colour_mix(pad):
    """
    Draw a simple dialog box with three sliders, so that the Red , Green & Blue
    brightness of the whole launchpad can be controlled.
    Only update the launchpad colour when a slider changes
    :return:
    """
    layout = [[PyGui.Text('Adjust the sliders for Red, Green & Blue levels. Click Cancel to exit.')],

              [PyGui.Slider(range=(0, 63), orientation='v', size=(12, 20), default_value=0),
               PyGui.Slider(range=(0, 63), orientation='v', size=(12, 20), default_value=0),
               PyGui.Slider(range=(0, 63), orientation='v', size=(12, 20), default_value=0)],
              [PyGui.Button('Ok'), PyGui.Button('Cancel')]
              ]

    # Create the Window
    window = PyGui.Window('Launchpad Colour Mixer', layout)
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
            set_wash_fast(pad, values[0], values[1], values[2])
        if event in (None, 'Cancel', 'Ok'):  # if user closes window or clicks cancel
            break
    print(values)

    window.close()


if __name__ == "__main__":
    launchpad = pylp.get_me_a_pad()
    colour_mix(launchpad)
