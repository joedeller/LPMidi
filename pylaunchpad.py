"""
Inspired by the work found at https://github.com/FMMT666/launchpad.py
Re-written to use rtmidi instead of pygame, different bit twiddling for scrolling
Limited to Launchpad Mini and MK2
Spaces not tabs and more functionality in the base class to reuse methods
"""
import random
import sys
import time
import csv
import rtmidi  # This is met by python-rtmidi
import narrow_letters as nl
import wide_font as wf
import platform


class LPMidi(object):
    """
    Try and find a Launchpad MK2 or Mini on the list of Midi ports
    """

    def __init__(self):
        if platform.system() =="Darwin":
            self.launchpads = ['Launchpad Mini MK3 LPMiniMK3 MIDI', 'MK2', 'Launchpad MK3', 'Launchpad Pro']
        else:
            self.launchpads = ['(LPMiniMK3', 'MK2',  'Launchpad MK3', 'Launchpad Pro']
        self.midi_out_port = None
        self.out_port_num = None
        self.midi_in_port = None
        self.in_port_num = None
        self.name = None

    def find_connected_launchpad(self):
        """
        TODO - Not yet fully working for MiniMk3
        First we have to check if there are any Launchpads connected.
        Only Launchpads in the list self.launchpads will be detected
        Currently only the first launchpad detected will be used

        :raises: IOError if we can't find a suitable launchpad
        :return:
        """
        # TODO - Allow for multiple devices
        # Start by getting a list of the Midi ports that rtmidi knows about
        midi_out = rtmidi.MidiOut()
        out_ports = midi_out.get_ports()
        midi_in = rtmidi.MidiIn()
        in_ports = midi_in.get_ports()

        # Use a list comprehension to scan the list of launchpad names in the list of output ports
        connected_pad = [port for port in out_ports if any(pad in port for pad in self.launchpads)]
        if connected_pad:
            self.name = connected_pad[0]
            self.out_port_num = out_ports.index(connected_pad[0])
            print(f"Found a {self.name} connected to output port {self.out_port_num}")
            print("Now checking midi input ports...")
            # We should always have a launchpad connected to midi in and out, it should be the same one
            # but it is possible to have a different device on input and output, so although we
            # could simply scan for the device name we just found, explicitly check again.
            pad_input = [s for s in in_ports if any(pad in s for pad in self.launchpads)]
            if pad_input:
                self.in_port_num = in_ports.index(pad_input[0])
                print(f"Found a {pad_input[0]} connected to input port {self.in_port_num}")
            del midi_out
        else:
            # No launchpad found
            print("I couldn't find any attached launchpads. Raising IOError")
            del midi_out
            raise IOError
        return self.out_port_num

    def find_launchpad_out_port(self):
        """
        Try and find a launchpad, if so set the midi out port and name
        Although a list comp might seem obvious, there are issues in that Launchpads have several Midi ports
        Need to figure out the canonical midi port to use, it appears to be different for MK3 / MK2  /Pro
        :return: The output port number the launchpad is connected to
        """
        # BUGBUG - If a LP Pro is connected, this code chooses the wrong port
        out_ports = rtmidi.MidiOut()
        ports = out_ports.get_ports()
        port_num = None
        found = False
        for (port_num, port) in enumerate(ports):
            for pad_name in self.launchpads:
                if pad_name in port:
                    found = True
                    self.name = pad_name
                    break
            if found:
                break

        if found:
            self.out_port_num = port_num
        else:
            port_num = None
        # Clean up as the Launchpad is going to need the midi port
        del out_ports

        return port_num

    def find_launchpad_in_port(self):
        """
        Try and find the Launchpad midi input launchpad
        :return:
        """
        in_ports = rtmidi.MidiIn()
        ports = in_ports.get_ports()
        port_num = None
        found = False
        for (port_num, port) in enumerate(ports):
            for pad_name in self.launchpads:
                if pad_name in port:
                    found = True

                    break
            if found:
                break
        if found:
            self.in_port_num = port_num

        else:
            port_num = None
        # Clean up as the Launchpad is going to need the midi port
        del in_ports
        return port_num


class LaunchpadBase(object):
    """
    The base class for our Launchpad objects, which contains most of the functionality
    Where devices differ, such as different button numbers or amount of colours supported
    Then the child objects will override the parent methods where necessary
    """

    def __init__(self, name, out_port_num, in_port_num):
        self.out_port_num = out_port_num
        self.in_port_num = in_port_num
        self.lp_midi_out_port = None
        self.lp_midi_in_port = None
        self.in_ports = None  # Need this for the midi input callback
        self.colours = {}
        self.red = 0  # For LP mini that only has red and green LEDS
        self.green = 0
        self.blue = 0
        self.name = name
        self.draw_colour = None
        self.frame_buffer = [0] * 8
        # Make a frame buffer for our painter code so we can save our drawings, up to 10 row of 10 pads for Pro
        self.painter_frame = [[0 for _ in range(9)] for _ in range(9)]  # Somewhere to store our painter picture
        self.SCROLL_NONE = 0
        self.SCROLL_LEFT = -1
        self.SCROLL_RIGHT = 1
        self.delay_time = 0.1
        self.set_colour_list()
        self.callback_count = 0
        self.last_x = None
        self.last_y = None
        self.max_x = 8  # Mini / MK2 have 9 leds, 0-8, Launchpad Pro has 10, 0-9
        self.painter_palette = [55, 55, 55], [55, 0, 0], [0, 55, 0], \
                               [0, 0, 55], [55, 55, 0], [0, 55, 55], [44, 33, 12], [0, 0, 0]

    def __delete__(self):
        self.close()

    def clear_frame_buffer(self):
        self.frame_buffer = [0] * 8

    def set_colour_list(self):
        """
        The MK2 has RGB, but the Mini only has RG, so more limited in what it can display
        :return:
        """
        name = self.name.lower()
        if "minimk3" in name or "mk2" in name or "pro" in name or "launchpad mk3" in name:
            self.colours = {'black': 0, 'off': 0, 'white': 119, 'red': 5, 'green': 17, 'blue': 44,
                            'orange': 84, 'purple': 55, 'brown': 105, 'lime': 75,
                            'pink': 56, 'yellow': 108, 'grey': 117}
        elif "mini" in self.name.lower():
            self.colours = {'black': 0, 'off': 0, 'red': 3, 'yellow': 49, 'green': 48, 'orange': 51}

    def colour_to_number(self, colour):
        colour = colour.lower()
        if colour in self.colours:
            return self.colours[colour]
        else:
            print(f"I don't know how to show {colour} yet, please update set_colour() in  pylaunchpad.py")
            return 0

    def open(self):
        """
        Try and open the midi port connected to the Launchpad
        :return:
        """
        # TODO - Wrap this in a try catch
        out_ports = rtmidi.MidiOut()
        self.lp_midi_out_port = out_ports.open_port(self.out_port_num)
        self.in_ports = rtmidi.MidiIn()
        self.lp_midi_in_port = self.in_ports.open_port(self.in_port_num)

    def close(self):
        # Release the midi port for other applications
        del self.lp_midi_out_port
        del self.lp_midi_in_port

    def reset(self):
        pass

    def programmer_mode(self):
        pass

    def limit(self, n, minimum, maximum):
        """
        Limit a number within the specified minimum and maximum values
        :param n:
        :param minimum:
        :param maximum:
        :return:
        """
        return max(min(maximum, n), minimum)

    def is_number(self, value):
        try:
            _ = float(value)
        except ValueError:
            return False
        return True

    def decode_button_message(self, msg):
        """
        To be implemented by child classes, take a midi message and return the X and Y coordinates
        :param msg:
        :return: an X and a Y coordinate
        """
        return 0, 0

    def midi_in_cb(self, msg, data):
        """
        A callback method for handling button inputs
        Note you cannot have a callback active and then manually read the midi input
        :param msg: A tuple of midi message and time received
        :param data: Not used, but needed for callback function signature
        :return:
        """
        print(f"Call back got {msg}")
        msg = msg[0]  # Don't care about the time stamp data in msg
        # Only do something for button down messages
        if len(msg) < 3:
            return
        state = msg[2]
        if state > 0:
            x, y = self.decode_button_message(msg)

            number = str(x)
            self.draw_char(nl.letters[number])
            time.sleep(.3)
            self.draw_char(nl.letters['.'])
            time.sleep(.3)
            number = str(y)
            self.draw_char(nl.letters[number])
            time.sleep(.3)

    def setup_painter_colours(self):
        self.reset()
        for x, colour in enumerate(self.painter_palette):
            r, g, b = colour
            self.set_led_xy(x, 0, r, g, b)
        self.last_y = 0
        self.last_x = 0
        self.red, self.green, self.blue = self.painter_palette[0]

    def random_paint(self, msg, data):
        msg = msg[0]  # Don't care about the time stamp data in msg
        # Only do something for button down messages
        print(msg)
        if len(msg) < 3:
            return
        state = msg[2]
        print(state)
        colour = "off"
        while colour == "off" or colour == "black":  # We don't want an "off" colour
            colour = random.choice(list(self.colours.keys()))
        if state > 0:
            print(colour)
            x, y = self.decode_button_message(msg)
            self.set_led_xy_by_colour(x, y, colour)
            self.last_y = y
            self.last_x = x

    def paint_app(self, msg, data):
        """
        A simple drawing routine
        :param msg:
        :param data:
        :return:
        """
        msg = msg[0]  # Don't care about the time stamp data in msg
        # Launchpad Pro has some additional messages, which are [208,0], must discard these
        if len(msg) < 3:
            return

        # Launchpad Pro has velocity in msg[2] and also has an extra "X" column to the left
        state = msg[2]
        print(state)
        # Fix for Launchpad Pro which has velocity, LP Mk2 just sends 127 for on
        if state > 0:
            # print(f"state is {state}")
            x, y = self.decode_button_message(msg)

            if y == 0 and x < 8:
                # Special case for PRO  as the top row starts at 1 as far as it is concerned:-(
                if "Launchpad Pro" in self.name:
                    x = x - 1
                self.red, self.green, self.blue = self.painter_palette[x]
            elif x != 8 or y != 8:
                self.set_led_xy(x, y, self.red, self.green, self.blue)
                # Pack the colours into a single value
                # NOTE - This uses 24 bits for RGB, but could use a 6 bit per colour format
                print(f"X:{x},Y:{y}")
                self.painter_frame[y][x] = (self.red << 16) + (self.green << 8) + self.blue
            self.last_y = y
            self.last_x = x

    def draw_letter(self, char, x_start=0, y_start=1, columns=8, clear=True):
        # Note that the Launchpad has a midi message designed for drawing and scrolling characters
        # but writing our own lets us use different fonts
        if ord(char) < 32 or ord(char) > 163:
            print("Sorry I don't know how to draw that character.")
            return
        char_data = nl.letters[char]
        self.draw_char(char_data, x_start, y_start, columns, clear)

    def draw_char(self, char_data, x_start=0, y_start=1, columns=8, clear=True):
        """
        Draw and 8*8 character. The data is not checked, it must consist of 8 numbers between 0 & 255
        The character is drawn from row 1, the start of the square buttons
        :param y_start:
        :param char_data: list of  byte_count of data, one per row
        :param x_start: X coordinate
        :param clear : if starting at x > 0, clear out the previous column data or not
        :param columns: how many columns of the character to draw
        :return:
        """
        # TODO - Consider using the faster sysex message with a series of byte_count
        # Work our way from top left down to bottom right
        for y in range(0, len(char_data)):
            data = int(char_data[y])
            if clear and x_start > 0:
                data = data >> x_start
                offset = 0
            else:
                offset = x_start

            for x in range(columns - offset):
                # We have a decimal number that must be translated to binary.
                # Take our data and use a "AND" mask comparing a single bit at each of the 8 bits
                mask = 128 >> x
                if data & mask:
                    self.set_led_xy_by_colour(x + offset, y + y_start, self.draw_colour)
                else:
                    self.set_led_xy_by_colour(x + offset, y + y_start, 'off')

    def draw_row(self, row_data, row, erase_previous=False):
        for x in range(0, 9):
            # We have a decimal number that must be translated to binary.
            # Take our data and use a "AND" mask comparing a single bit at each of the 8 bits
            # Don't over write if bit is zero
            mask = 128 >> x
            if row_data & mask:
                self.set_led_xy_by_colour(x, row, self.draw_colour)
            if row == 0 and erase_previous:
                self.set_led_xy_by_colour(x, row, 0)

    def set_led_xy(self, x, y, red, green, blue):
        pass

    def set_led_xy_by_colour(self, x, y, colour_code=None):
        """
        This will be overridden by the specific launchpad type sub classes
        :param x:
        :param y:
        :param colour_code:
        :return:
        """

        pass

    def scroll_on_right(self, char_data):
        """
        Scroll a character from the left to the right of the launchpad
        :param char_data: 8 byte_count of bitmap data, 1 per row
        :return:
        """
        for column in range(8):

            for row in range(8):
                bit_mask = 1 << column  # Start at LSB and shift left
                # shift whatever is in the frame buffer along one column
                self.frame_buffer[row] = self.frame_buffer[row] >> 1
                new_data = char_data[row] & bit_mask
                new_data = new_data << (7 - column)
                row_data = new_data | self.frame_buffer[row]
                self.frame_buffer[row] = row_data

            self.draw_char(self.frame_buffer)
            time.sleep(self.delay_time)

    def scroll_frames_right(self, frame_data):
        """
        Given a series of frames, scroll on from right and fully off again
        :param frame_data: list of frames where each is 8 bytes of data, each byte one row of mono pixels
        :return:
        """
        frame_count = len(frame_data)
        current_frame = 0
        for column in range(8):
            char_data = frame_data[current_frame]
            # as column goes up, we want 1 bit, 2 bits, 3 bits, 4 bits ....
            for row in range(8):
                # 2*column 0,2,4,8,16,32,64,128  + 1
                bit_mask = (2 << column) - 1  # Start at LSB and shift left
                new_data = char_data[row] & bit_mask
                new_data = new_data << (7 - column)
                self.frame_buffer[row] = new_data
            self.draw_char(self.frame_buffer)
            time.sleep(self.delay_time)

            current_frame += 1
            if current_frame > frame_count - 1:
                current_frame = 0

        # Now scroll off, use the starting column parameter of draw_char...
        for column in range(1, 8):
            self.draw_char(frame_data[current_frame], column)
            current_frame += 1
            if current_frame > frame_count - 1:
                current_frame = 0
            time.sleep(self.delay_time)
        self.draw_char(nl.letters[' '])
        # Tidy up the frame buffer so it is empty
        self.clear_frame_buffer()

    def scroll_on_left(self, char_data):
        """
        Scroll a character from the right to the left of the launchpad
        :param char_data: 8 byte_count of bitmap data, 1 byte per row
        :return:
        """

        for column in range(8):
            bit_mask = 128 >> column  # Start at MSB and shift right
            for row in range(8):
                self.frame_buffer[row] = self.frame_buffer[row] << 1
                new_data = char_data[row] & bit_mask
                new_data = new_data >> (7 - column)
                row_data = new_data | self.frame_buffer[row]
                self.frame_buffer[row] = row_data

            self.draw_char(self.frame_buffer)
            time.sleep(self.delay_time)

    def scroll_up(self, message):
        """
        Scroll a series of characters from the bottom to the top of the launchpad
        No bit twiddling needed
        :param message: A string of characters
        :return:
        """
        message = " " + message + " "
        full_bitmap = []
        for char in message:
            full_bitmap += nl.letters[char]  # Build an array with all of the data for all of the letters
            full_bitmap += [0]
        for i in range(len(full_bitmap)):
            self.draw_char(full_bitmap[i:i + 8])
            time.sleep(self.delay_time)

    def scroll_message(self, message, direction=None, wide=False):
        """
        Scroll a series of characters from the left or the right
        :param message: A series of characters to display
        :param direction: From the left or right. If scrolling to the right the message is reversed
        :param bool wide: Set to True to use a Wide font
        :return:
        """
        message = f" {message}  "  # extra space leaves the launchpad empty when message has scrolled
        if direction is None:
            direction = self.SCROLL_LEFT

        if direction == self.SCROLL_RIGHT:
            message = message[::-1]
            for i in range(len(message)):
                if wide:
                    char = nl.letters[message[i]]
                else:
                    char = wf.letters[message[i]]
                self.scroll_on_right(char)

        else:
            for i in range(len(message)):
                if wide:
                    char = nl.letters[message[i]]
                else:
                    char = wf.letters[message[i]]
                self.scroll_on_left(char)


class LaunchpadPro(LaunchpadBase):
    """
    Support for the Launchpad Pro (experimental, not all working yet)
    """

    def __init__(self, name, out_port_num, in_port_num):
        super(LaunchpadPro, self).__init__(name, out_port_num, in_port_num)
        print("Launchpad Pro startup")
        # The PRO has a bigger frame, so we need a larger storage space for our picture
        self.painter_frame = [[0 for _ in range(10)] for _ in range(10)]
        self.max_x = 9

    def set_all_on(self, red, green, blue):
        """
        Special sysex for orginal Launchpad Pro
        :param red:
        :param green:
        :param blue:
        :return:
        """

        msg = [240, 0, 32, 41, 2, 16, 15, 0] + [red, green, blue] * 99 + [247]
        self.lp_midi_out_port.send_message(msg)

    def decode_button_message(self, msg):
        button_number = msg[1]
        pressed = False
        x = button_number % 10
        y = int((99 - button_number) / 10)
        print(f"X: {x} Y: {y} Pressed = {pressed}")
        return x, y

    @staticmethod
    def xy_to_number(x, y):
        """
        Convert an x,y coordinate to an LED number
        :param x:
        :param y:
        :return:
        """
        # The pro misses out buttons 0, 9, 90, where there could be buttons but aren't
        if x < 0 or x > 9 or y < 0 or y > 9:
            print(f"{x}, {y}")
            raise ValueError
        # top row (round buttons) check
        if y == 0 and x > 7:
            print(f"{x}, {y}")
            raise ValueError
        # bottom row check
        if y == 9 and 1 <= x > 7:
            print(f"{x}, {y}")
            raise ValueError
        if y == 0:
            led = 91 + x
        elif y == 9:
            led = x
        else:
            # swap y
            led = 90 - (10 * y) + x
        return led

    def set_led_xy(self, x, y, red, green, blue):
        """
        Set an LED at coordinate X,Y, to the specified RGB colour
        :param x:
        :param y:
        :param red: 0 - 63
        :param green: 0 - 63
        :param blue: 0 - 63
        :return:
        """

        try:
            led = self.xy_to_number(x, y)
        except ValueError:
            return

        red = self.limit(red, 0, 63)
        green = self.limit(green, 0, 63)
        if blue is None:
            blue = 0
        else:
            blue = self.limit(blue, 0, 63)

        # needs a sysex message , so wrap with byte_count 240 and 247
        self.lp_midi_out_port.send_message([240, 0, 32, 41, 2, 16, 11, led, red, green, blue, 247])
        # self.lp_midi_out_port.send_message([240, 0, 32, 41, 2, 24, 11, led, red, green, blue, 247])

    def set_led_by_number(self, number, color_code):
        if not self.is_number(color_code):
            color_code = self.colour_to_number(color_code)
        self.lp_midi_out_port.send_message([144, number, color_code])

    def led_all_on(self, colour_code):
        """
        Turn all of the LEDs on to a specific colour
        :param colour_code:
        :return:
        """
        if colour_code is None:
            colour_code = 'green'
        if not self.is_number(colour_code):
            # Try and find the text string in self.colours
            colour_code = self.colour_to_number(colour_code)

        if colour_code is None:
            colour_code = self.colours['white']
        else:
            colour_code = min(colour_code, 127)
            colour_code = max(colour_code, 0)

        self.lp_midi_out_port.send_message([240, 0, 32, 41, 2, 16, 14, colour_code, 247])

    def set_led_xy_by_colour(self, x, y, colour_code=48):

        """
        Although we lose the ability to use RGB, using a single byte colour code means we
        can send a three byte message rather than a system exclusive one, so is a bit faster
        On the LP Mini we have a limited colour palette anyway
        :param x:
        :param y:
        :param colour_code: 0-127
        :return:
        """

        try:
            led = self.xy_to_number(x, y)
            self.set_led_by_number(led, colour_code)
        except ValueError:
            pass

    def reset(self):
        """
        Turn all LEDs OFF
        :return:
        """
        self.last_y = 0
        self.last_x = 0
        self.led_all_on(0)


class LaunchpadMk2(LaunchpadBase):
    """
    For Launchpad Mark 2 with RGB displays
    """

    # LED AND BUTTON NUMBERS IN RAW MODE (DEC)
    #
    #        +---+---+---+---+---+---+---+---+
    #        |104|   |106|   |   |   |   |111|
    #        +---+---+---+---+---+---+---+---+
    #
    #        +---+---+---+---+---+---+---+---+  +---+
    #        | 81|   |   |   |   |   |   |   |  | 89|
    #        +---+---+---+---+---+---+---+---+  +---+
    #        | 71|   |   |   |   |   |   |   |  | 79|
    #        +---+---+---+---+---+---+---+---+  +---+
    #        | 61|   |   |   |   |   | 67|   |  | 69|
    #        +---+---+---+---+---+---+---+---+  +---+
    #        | 51|   |   |   |   |   |   |   |  | 59|
    #        +---+---+---+---+---+---+---+---+  +---+
    #        | 41|   |   |   |   |   |   |   |  | 49|
    #        +---+---+---+---+---+---+---+---+  +---+
    #        | 31|   |   |   |   |   |   |   |  | 39|
    #        +---+---+---+---+---+---+---+---+  +---+
    #        | 21|   | 23|   |   |   |   |   |  | 29|
    #        +---+---+---+---+---+---+---+---+  +---+
    #        | 11|   |   |   |   |   |   |   |  | 19|
    #        +---+---+---+---+---+---+---+---+  +---+
    #
    #
    #
    # LED AND BUTTON NUMBERS IN XY MODE (X/Y)
    #
    #          0   1   2   3   4   5   6   7      8
    #        +---+---+---+---+---+---+---+---+
    #        |0/0|   |2/0|   |   |   |   |   |         0
    #        +---+---+---+---+---+---+---+---+
    #
    #        +---+---+---+---+---+---+---+---+  +---+
    #        |0/1|   |   |   |   |   |   |   |  |   |  1
    #        +---+---+---+---+---+---+---+---+  +---+
    #        |   |   |   |   |   |   |   |   |  |   |  2
    #        +---+---+---+---+---+---+---+---+  +---+
    #        |   |   |   |   |   |5/3|   |   |  |   |  3
    #        +---+---+---+---+---+---+---+---+  +---+
    #        |   |   |   |   |   |   |   |   |  |   |  4
    #        +---+---+---+---+---+---+---+---+  +---+
    #        |   |   |   |   |   |   |   |   |  |   |  5
    #        +---+---+---+---+---+---+---+---+  +---+
    #        |   |   |   |   |4/6|   |   |   |  |   |  6
    #        +---+---+---+---+---+---+---+---+  +---+
    #        |   |   |   |   |   |   |   |   |  |   |  7
    #        +---+---+---+---+---+---+---+---+  +---+
    #        |   |   |   |   |   |   |   |   |  |8/8|  8
    #        +---+---+---+---+---+---+---+---+  +---+
    #

    def programmer_mode(self):
        self.lp_midi_out_port.send_message([240, 0, 32, 41, 2, 24, 34, 0, 247])

    def led_all_on(self, colour_code='green'):
        """
        Turn all of the LEDs on to a specific colour
        :param colour_code:
        :return:
        """
        # BUG BUG - Single sysex message Not implemented on the MK3
        if not self.is_number(colour_code):
            # Try and find the text string in self.colours
            colour_code = self.colour_to_number(colour_code)

        if colour_code is None:
            colour_code = self.colours['white']
        else:
            colour_code = min(colour_code, 127)
            colour_code = max(colour_code, 0)
        for led in range(11, 112):
            self.set_led_by_number(led, colour_code)

    def set_all_on(self, red, green, blue):
        red = int(red)
        green = int(green)
        blue = int(blue)

        base_msg = [240, 0, 32, 41, 2, 24, 11]
        for led in range(11, 71):
            base_msg.append(led)
            base_msg.append(red)
            base_msg.append(green)
            base_msg.append(blue)
        base_msg.append(247)
        self.lp_midi_out_port.send_message(base_msg)
        base_msg = [240, 0, 32, 41, 2, 24, 11]
        for led in range(71, 111):
            base_msg.append(led)
            base_msg.append(red)
            base_msg.append(green)
            base_msg.append(blue)
        base_msg.append(247)
        self.lp_midi_out_port.send_message(base_msg)

    def reset(self):
        """
        Turn all LEDs OFF
        :return:
        """
        self.last_y = 0
        self.last_x = 0
        self.lp_midi_out_port.send_message([240, 0, 32, 41, 2, 24, 14, 0, 247])

    def set_led_by_number(self, number, color_code):

        if color_code is None:
            color_code = 'green'

        if not self.is_number(color_code):
            color_code = self.colour_to_number(color_code)

        number = min(number, 111)
        number = max(number, 0)
        # If number is between 90 and 104, there is no matching LED so just return
        if 89 < number < 104:
            return

        if self.draw_colour is None:
            self.draw_colour = self.colours['red']

        if number < 104:
            self.lp_midi_out_port.send_message([144, number, color_code])
        else:
            self.lp_midi_out_port.send_message([176, number, color_code])

    def set_led_xy_by_colour(self, x, y, colour_code=None):

        """
        Although we lose the ability to use RGB, using a single byte colour code means we
        can send a three byte message rather than a system exclusive one, so is a bit faster
        On the LP Mini we have a limited colour palette anyway
        :param x:
        :param y:
        :param colour_code: 0-127
        :return:
        """
        if colour_code is None:
            colour_code = 'green'
        if x < 0 or x > 8 or y < 0 or y > 8:
            return
        led = self.xy_to_number(x, y)
        self.set_led_by_number(led, colour_code)

    def xy_to_number(self, x, y):
        """
        Convert an x,y coordinate to an LED number
        :param x:
        :param y:
        :return:
        """
        # top row (round buttons)
        if y == 0:
            led = 104 + x
        else:
            # swap y
            led = 91 - (10 * y) + x
        return led

    def set_led_xy(self, x, y, red, green, blue):
        """
        Set an LED at coordinate X,Y, to the specified RGB colour
        :param x:
        :param y:
        :param red: 0 - 63
        :param green: 0 - 63
        :param blue: 0 - 63
        :return:
        """

        if x < 0 or x > 8 or y < 0 or y > 8:
            return

        led = self.xy_to_number(x, y)
        red = self.limit(red, 0, 63)
        green = self.limit(green, 0, 63)
        if blue is None:
            blue = 0
        else:
            blue = self.limit(blue, 0, 63)

        # needs a sysex message , so wrap with byte_count 240 and 247
        self.lp_midi_out_port.send_message([240, 0, 32, 41, 2, 16, 11, led, red, green, blue, 247])

    def button_state_xy(self):
        """
        Scan to see if any buttons are pressed
        :return:
        """

        msg = self.lp_midi_in_port.get_message()

        if msg:
            # 127 means pressed, 0 means released
            self.decode_button_message(msg[0])
        time.sleep(0.01)

    def decode_button_message(self, msg):
        x, y = 0, 0
        msg_type = msg[0]
        button_number = msg[1]
        msg_data = msg[2]
        pressed = False
        print(f"msg {msg_type}, data = {msg_data}, button {button_number}")
        if msg_type == 144:
            x = (button_number % 10) - 1
            y = 9 - int(button_number / 10)
        elif msg_type == 176:
            x, y = button_number - 104, 0
        if msg_data > 0:
            pressed = True

        print(f"X: {x} Y: {y} Pressed = {pressed}")
        return x, y


class LaunchpadMiniMk3(LaunchpadMk2):
    """
    The LP mini MK3 is similar to the Launchpad MK2, but with some notable differences.
    """

    def programmer_mode(self):
        # self.lp_midi_out_port.send_message([240, 0, 32, 41, 2, 24, 14, colour_code, 247])
        self.lp_midi_out_port.send_message([240, 0, 32, 41, 2, 13, 14, 1, 247])

    def reset(self, colour=0):
        """
        No global reset message, so doing this the slow way
        Could use a RGB style message
        :param colour:
        :return:
        """
        self.last_y = 0
        self.last_x = 0
        if colour == 0:
            self.set_all_on(0, 0, 0)
            return
        # If we have a specific colour, then use the slower method
        for x in range(9):
            for y in range(9):
                self.set_led_xy_by_colour(x, y, colour)

    def set_all_on_slow(self, red, green, blue):
        for x in range(9):
            for y in range(9):
                self.set_led_xy(x, y, red, green, blue)

    def set_all_on(self, red, green, blue):
        base_msg = [240, 0, 32, 41, 2, 13, 3]
        for led in range(11, 100):
            base_msg.append(3)  # 3 is static, followed by R,G,B
            base_msg.append(led)
            base_msg.append(red)
            base_msg.append(green)
            base_msg.append(blue)
        base_msg.append(247)
        self.lp_midi_out_port.send_message(base_msg)
        return

    def set_led_xy(self, x, y, red, green, blue):
        """
        Set an LED at coordinate X,Y, to the specified RGB colour
        :param x:
        :param y:
        :param red: 0 - 63
        :param green: 0 - 63
        :param blue: 0 - 63
        :return:
        """

        if x < 0 or x > 8 or y < 0 or y > 8:
            return

        led = self.xy_to_number(x, y)
        red = int(self.limit(red, 0, 63))
        green = int(self.limit(green, 0, 63))
        if blue is None:
            blue = 0
        else:
            blue = int(self.limit(blue, 0, 63))
        # needs a sysex message , so wrap with byte_count 240 and 247
        self.lp_midi_out_port.send_message([240, 0, 32, 41, 2, 13, 3, 3, led, red, green, blue, 247])

    def set_led_by_number(self, number, color_code=None):

        if not self.is_number(color_code):
            color_code = self.colour_to_number(color_code)

        number = min(number, 111)
        number = max(number, 0)

        if self.draw_colour is None:
            self.draw_colour = self.colours['red']

        if number < 90:
            self.lp_midi_out_port.send_message([144, number, color_code])
        else:
            self.lp_midi_out_port.send_message([176, number, color_code])

    def decode_button_message(self, msg):
        x, y = 0, 0
        msg_type = msg[0]
        button_number = msg[1]
        msg_data = msg[2]
        pressed = False
        print(f"msg {msg_type}, data = {msg_data}, button {button_number}")
        if msg_type == 144 or msg_type == 176:
            x = (button_number % 10) - 1
            y = 9 - int(button_number / 10)

        if msg_data > 0:
            pressed = True

        print(f"X: {x} Y: {y} Pressed = {pressed}")
        return x, y

    def xy_to_number(self, x, y):
        """
        Convert an x,y coordinate to an LED number
        :param x:
        :param y:
        :return:
        """
        # MK2 top row starts at 104, so if y is 0, button is 104 + x
        button = (9 - y) * 10
        button += x + 1
        return button


class LpMini(LaunchpadBase):
    """
    Original Launchpad Mini , limited to Red and Green colours
    """
    # LED AND BUTTON NUMBERS IN RAW MODE (DEC):
    #
    # +---+---+---+---+---+---+---+---+
    # |104|105|106|107|108|109|110|111| < Need to send msg 176, very confusing that button IDs are identical
    # +---+---+---+---+---+---+---+---+ < A keypress here will send a 176 message, not a 144
    #
    # +---+---+---+---+---+---+---+---+  +---+
    # |  0|...|   |   |   |   |   |  7|  |  8|
    # +---+---+---+---+---+---+---+---+  +---+
    # | 16|...|   |   |   |   |   | 23|  | 24|
    # +---+---+---+---+---+---+---+---+  +---+
    # | 32|...|   |   |   |   |   | 39|  | 40|
    # +---+---+---+---+---+---+---+---+  +---+
    # | 48|...|   |   |   |   |   | 55|  | 56|
    # +---+---+---+---+---+---+---+---+  +---+
    # | 64|...|   |   |   |   |   | 71|  | 72|
    # +---+---+---+---+---+---+---+---+  +---+
    # | 80|...|   |   |   |   |   | 87|  | 88|
    # +---+---+---+---+---+---+---+---+  +---+
    # | 96|...|   |   |   |   |   |103|  |104|
    # +---+---+---+---+---+---+---+---+  +---+
    # |112|...|   |   |   |   |   |119|  |120|
    # +---+---+---+---+---+---+---+---+  +---+
    #
    #
    # LED AND BUTTON NUMBERS IN XY MODE (X/Y)
    #
    #   0   1   2   3   4   5   6   7      8
    # +---+---+---+---+---+---+---+---+
    # |   |1/0|   |   |   |   |   |   |         0
    # +---+---+---+---+---+---+---+---+
    #
    # +---+---+---+---+---+---+---+---+  +---+
    # |0/1|   |   |   |   |   |   |   |  |   |  1
    # +---+---+---+---+---+---+---+---+  +---+
    # |   |   |   |   |   |   |   |   |  |   |  2
    # +---+---+---+---+---+---+---+---+  +---+
    # |   |   |   |   |   |5/3|   |   |  |   |  3
    # +---+---+---+---+---+---+---+---+  +---+
    # |   |   |   |   |   |   |   |   |  |   |  4
    # +---+---+---+---+---+---+---+---+  +---+
    # |   |   |   |   |   |   |   |   |  |   |  5
    # +---+---+---+---+---+---+---+---+  +---+
    # |   |   |   |   |4/6|   |   |   |  |   |  6
    # +---+---+---+---+---+---+---+---+  +---+
    # |   |   |   |   |   |   |   |   |  |   |  7
    # +---+---+---+---+---+---+---+---+  +---+
    # |   |   |   |   |   |   |   |   |  |8/8|  8
    # +---+---+---+---+---+---+---+---+  +---+

    def reset(self):
        self.last_y = 0
        self.last_x = 0
        self.lp_midi_out_port.send_message([176, 0, 0])

    def get_led_color(self, red, green):
        """
        Convert the red and green brightness to a single launchpad LED compatible value
        :param red: 0-3, which translates to 0-7 in possible binary brightness
        :param green: 0-3
        :return:
        """
        led = 0
        red = self.limit(red, 0, 3)
        green = self.limit(green, 0, 3)
        led |= red  # First 3 bits of the LED value control the Red brightness
        led |= green << 4  # The Green brightness starts at bit 4, so shift the value left then OR it
        return led

    def set_led_xy_by_colour(self, x, y, colour=None):
        """
        Note that this doesn't appear to be working for top row buttons, Y = 0
        :param x:
        :param y:
        :param colour:
        :return:
        """
        if not self.is_number(colour):
            # Try and find the text string in self.colours
            colour = self.colour_to_number(colour)

        led_id = self.xy_to_number(x, y)
        if y == 0:
            self.lp_midi_out_port.send_message([240, 176, 104 + x, colour, 247])
        else:
            self.lp_midi_out_port.send_message([144, led_id, colour])

    def set_led_by_number(self, led_id, red, green):

        colour = self.get_led_color(red, green)
        # Special case for top row buttons, need to send a different message
        # Due to the top row also being button IDs, 104-111 we have to subtract the extra 100 we
        # added previously to avoid confusion.

        if led_id > 199 & led_id < 208:
            self.lp_midi_out_port.send_message([176, led_id - 100, colour])
        else:
            self.lp_midi_out_port.send_message([144, led_id, colour])

    def set_led_xy(self, x, y, red, green, blue=None):
        """
        Set a LED by the supplied X & Y co-ordinates
        :param x: 0 to 8 (left to right)
        :param y:  0 to 8 (top to bottom)
        :param red: brightness 0 to 3
        :param green:
        :param blue: Ignored for the original lP mini which doesn't have blue
        :return:
        """
        if x < 0 or x > 8 or y < 0 or y > 8:
            return

        led_id = self.xy_to_number(x, y)
        self.set_led_by_number(led_id, red, green)

    def xy_to_number(self, x, y):
        # Convert the X,Y to a single number. Top 4 bits are the Y value, bottom 4 bits are X
        # Somewhat confusingly on the LPMini, the top row are 104 + X, but need a different midi message
        # We work around this by setting the number to 204 + x, then removing 100 later
        if y == 0:
            led_id = 204 + x
        else:
            y = y - 1
            led_id = y << 4
            led_id = led_id | x
        return led_id

    def button_state_xy(self):
        """
        Scan to see if any buttons are pressed
        :return:
        """

        msg = self.lp_midi_in_port.get_message()

        if msg:
            msg = msg[0]

            # 127 means pressed, 0 means released
            self.decode_button_message(msg)

        time.sleep(0.01)

    def decode_button_message(self, msg):
        """
        Translate the midi message into X/Y coordinates and a button state
        :param msg:
        :return:
        """
        x, y = 0, 0
        msg_type = msg[0]
        button_number = msg[1]
        msg_data = msg[2]
        pressed = False
        print(f"msg type {msg_type}, button number {button_number}")
        if msg_type == 144:
            x = button_number & 0x0f
            y = 1 + (button_number >> 4)
        elif msg_type == 176:  # Top Row
            x, y = button_number - 104, 0

        if msg_data > 0:
            pressed = True

        print(f"X: {x} Y: {y} Pressed = {pressed}")
        return x, y


def rgb_from_int(rgb):
    """
    Unpack a 24bit RGB value into its components. We could use fewer bits as Launchpads use 6 bit colours
    But 18 bits is still three bytes, so there isn't a lot of point
    :param rgb:
    :return:
    """
    blue = rgb & 255
    green = (rgb >> 8) & 255
    red = (rgb >> 16) & 255
    return red, green, blue


def save_frame(frame, filename="my_picture.csv"):
    """
    Store a the frame bitmap to a CSV file, will overwrite any previously saved file
    :param frame: the launchpad self.painter_frame bitmap
    :param filename: Name of the file to save the data
    :return:
    """
    # TODO - Handle IO errors
    with open(filename, "w+", newline="") as my_csv:
        csv_writer = csv.writer(my_csv, delimiter=',')
        csv_writer.writerows(frame)


def load_frame(pad, frame_file="my_picture.csv"):
    """
    Load a previously saved bitmap CSV file and draw it
    :param pad: A launchpad object
    :param frame_file: name of the file to load
    :return:
    """
    # TODO Handle IO errors
    with open(frame_file, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for y, row in enumerate(csv_reader):
            for x, value in enumerate(row):
                red, green, blue = rgb_from_int(int(value))
                pad.set_led_xy(x, y, red, green, blue)


def get_me_a_pad():
    """
    Try and find a connected launchpad, currently only a single launchpad is used
    :return: a Launchpad object
    """
    # Create a LaunchPad midi object to help us find the midi port a launchpad is connected to
    lp_midi = LPMidi()
    # Firstly find the port we can send messages to the Launchpad
    out_port = lp_midi.find_launchpad_out_port()
    # Now the port we will receive messages from
    in_port = lp_midi.find_launchpad_in_port()
    if out_port is not None:
        print(f"Midi out {out_port}, name {lp_midi.name}")
        if in_port is not None:
            print(f"Midi in {in_port}, name {lp_midi.name}")

    else:
        print("No Launchpad detected")
        sys.exit()
    # This code supports LaunchPad mini, Mini Mk3 or Launchpad Mk2
    # TODO put this in a lookup table
    if "MiniMK3" in lp_midi.name:
        pad = LaunchpadMiniMk3(lp_midi.name, out_port, in_port)
    elif "Launchpad MK3" in lp_midi.name:
        # Just for testing, no implementation yet
        pad = LaunchpadMiniMk3( lp_midi.name, out_port, in_port)
    elif "Mini" in lp_midi.name:
        pad = LpMini(lp_midi.name, out_port, in_port)
    elif "Pro" in lp_midi.name:
        pad = LaunchpadPro(lp_midi.name, lp_midi.out_port_num, lp_midi.in_port_num)
    else:
        pad = LaunchpadMk2(lp_midi.name, out_port, in_port)
    pad.draw_colour = pad.colours['red']
    # Connect up and reset the LaunchPad
    pad.open()

    pad.programmer_mode()
    pad.reset()
    return pad
