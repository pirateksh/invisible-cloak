# Invisible Cloak

_Get invisible using a magical cloak just like Harry Potter._

## Description - 

This is a simple yet very intriguing project made by Image Processing using OpenCV and Numpy.

## What actually (roughly) happens behind the scene?

* Camera captures inital background image for ~ 2 seconds.
* A color is chosen for processing.
* Real time Video Frames are captured and converted from BGR color space to HSV/HSB color space.
* It is then processed and all occurance of eariler chosen color (red) is replaced by the initial background image which we have captured earlier.
* For this a HSV/HSB range is defined  which is to be replaced. For red colour, Hue(H) = 0 - 10 and 170 - 180, Saturation(S) = 120 - 255 and Brightness(B) = 70 - 255.

## How to run?

* Clone the repository - `git clone https://github.com/pirateksh/invisible-cloak.git`
* Change directory to invisible-cloak `cd invisible-cloak`
* Run `python stream.py`
