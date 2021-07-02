import cProfile

import kaleidoscope
import kaleidoscopeArray
import cv2
from arrayIm import jpg2png
from PIL import Image

img = cv2.imread('test.jpg')
img = jpg2png(img)

cProfile.run("img = kaleidoscopeArray.kaleidoscope(img, mode = 2)")


img = Image.open('test.jpg')
img = img.crop((0,0,434,434))

cProfile.run("img = kaleidoscope.kaleidoscope(img)")

img = cv2.imread('test.jpg')
img = jpg2png(img)

cProfile.run("img = kaleidoscopeArray.kaleidoscope(img, mode = 2)")