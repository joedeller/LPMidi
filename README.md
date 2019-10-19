#Python interface to Novation Launchpad Mini MK3
 
This library is for the Novation Pop Up Shop Workshop sessions.


Inspired by the work found at https://github.com/FMMT666/launchpad.py

Re-written to use rtmidi instead of pygame, different bit twiddling for scrolling
This library supports a very limited set of Launchpad devices, currently only Launchpad Mini MK3 and Launchpad MK2
_STANDARD DISCLAIMER

The library comes without any warranty or support of any kind. It is not an officially supported Focusrite Novation
 project.  If it works for you that's great, but beyond that you are on your own :-(  Updates are likely to be
sporadic at best, but should you wish to fork the project or contribute, then by all means proceed!


## Setup

You wil need to install python-rtmidi to be able to use the pylaunchpad.py library
pip install python-rtmidi
The demos.py example file uses PySimpleGui, so if you plan to run that, install this as well.
pip install pysimplegui

Clone this repo and run demo.py for examples as to what can be done.


### Using pylaunchpad.py

The most simple code would be:
```python
import pylaunchpad as pylp
launchpad = pylp.get_me_a_pad()
launchpad.set_led_xy_by_colour(0, 0, launchpad.colours['red'])

```

To turn a pad off:
```python
import pylaunchpad as pylp
launchpad = pylp.get_me_a_pad()
launchpad.set_led_xy_by_colour(0, 0, launchpad.colours['off'])

```

The library has many "helper" functions to draw letters and bitmaps, as well as scroll characters on and off

#### Troubleshooting
If your launchpad is sat drawing patterns on its own, that normally means it hasn't enumerated correctly.
Sometimes python will hold the midi port open and not let go and you might need a reboot.
Make sure another program such as a DAW or sequencer isn't running at the same time.  The get_me_a_pad()
code should print out a list of midi ports and what it thinks the Launchpad is connected to.
Currently only a single Launchpad is supported. 

## FAQ
##### *What version of Python do I need?*
The code was written using Python 3.7

##### *What platforms are supported?*

The code was developed on Windows 10 64bit, but should also work on Mac OS Mojave. Not Mac OS Catalina has not
been tested.  Other platforms such as Windows 7 and 8 should work, as long as the rtmidi library is able to 
access midi ports on the host.

##### *What Launchpads does the code support?*

Launchpad Mini MK3 and Launchpad Mk2.  There is limited support for the Launchpad Mini due to it only having Red
and Green LEDs.

#### Where are the tests????
A good question and somewhat ironic as I test software for a living.


