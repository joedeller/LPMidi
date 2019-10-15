"""
Use the Launchpad to display binary numbers from 0 to 255
Use green to highlight when a bit is set to 1
"""

import sys
import time

import pylaunchpad as lp


def is_number(dec):
    try:
        _ = float(dec)
        return True

    except ValueError:
        print("Not a number")
        return False


def get_a_number():
    """
    Ask for user input
    :return:
    """
    no_data = True
    dec = 0
    while no_data:
        dec = input("Enter a Hex or decimal number 0 - 255, 'q' to quit : ")
        if "q" in dec:
            sys.exit(0)
        if "0x" in dec:
            dec = int(dec, 16)
        if is_number(dec):
            no_data = False
    return int(dec)


def convert_to_binary(decimal, byte_count=1):
    binary = bin(decimal)[2:].zfill(byte_count * 8)
    return binary


def count_up(pad):
    for number in range(0, 256):
        draw_binary(pad, number)
        time.sleep(0.1)


def main():
    pad = lp.get_me_a_pad()
    count_up(pad)
    while True:
        decimal = get_a_number()
        draw_binary(pad, decimal)


def draw_binary(pad, decimal):
    # TODO - Handle > 8 bits, use row 7 for 16 bit numbers
    blocks = convert_to_binary(decimal)
    # row 7 is MSB 8bits, row 8 is LSB
    msb = blocks[0:8]
    lsb = blocks[8:]

    draw_8_bits(pad, 7, msb)
    draw_8_bits(pad, 8, lsb)
    print(blocks)


def draw_8_bits(pad, row, blocks):
    for x, digit in enumerate(blocks):
        if digit == "1":
            pad.set_led_xy_by_colour(x, row, pad.colours['green'])
        else:
            pad.set_led_xy_by_colour(x, row, pad.colours['black'])


if __name__ == "__main__":
    main()
