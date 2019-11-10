# Python interface to Novation Launchpad Mini MK3
 
This library is for the Novation Pop Up Shop Workshop sessions.


Inspired by the work found at https://github.com/FMMT666/launchpad.py

Re-written to use rtmidi instead of pygame, different bit twiddling for scrolling
This library supports a very limited set of Launchpad devices, currently only Launchpad Mini MK3 and Launchpad MK2

*STANDARD DISCLAIMER*

The library comes without any warranty or support of any kind. It is not an officially supported Focusrite Novation
 project.  If it works for you that's great, but beyond that you are on your own :-(  Updates are likely to be
sporadic at best, but should you wish to fork the project or contribute, then by all means proceed!
See the LICENSE.txt file for more information

## Setup
Note: Requires Python 3.7x.  At the present time the python-rtmidi library is not compatible with 3.8.

Additional library requirements are in the requirements.txt file.  Pycharm will detect this and
offer to install the additional libraries.  Other IDEs may vary.
For manual install, you wil need to install python-rtmidi to be able to use the pylaunchpad.py library

From a command prompt / terminal: 
```
pip install python-rtmidi
````

The demos.py example file uses PySimpleGui, so if you plan to run that, install this as well.
```
pip install pysimplegui
````

Virtual environments are beyond the scope of this readme, but unless you have a good reason
not to use them, then they are a good idea.

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

Launchpad Mini MK3 and Launchpad Mk2 and Launchpad Pro.  There is limited support for the Launchpad Mini MK2 due to it only having Red and Green LEDs.  Note - for Launchpad Pro you must put the Launchpad into LIVE mode, press the setup button on the top left, then the green pad to enter Live Mode.


##### *What are the dependencies?*
The requirements.txt has a list of any additional libraries.

##### *Why aren't you using the Launchpad's own text scrolling feature?*
There are a range of LED matrix fonts on the net to suit and discovering how
the font data gets translated into pixels is well worth learning.
Using our own font routine allows reuse for drawing bitmaps

##### *Where are the tests????*
A good question and somewhat ironic as I test software for a living.
At the moment the code is tested manually against a Mini Mk3 and MK2
A manual, physical check on a real Launchpad is needed to verify the colour & position
of the pad being acted upon - writing a simulator would be a lot of work.



