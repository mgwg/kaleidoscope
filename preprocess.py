from kaleidoscope import kaleidoscope
from PIL import Image
import math

def gen_images(imagePath: str, dispDim: tuple = (1920, 1080),
               mode = 0, fineness: int = 200, n: int = 2) -> list:
    '''
    outputPath must include slash at end, if ends in 
    mode = kaleidoscope mode
    fineness = region of movement slice is stationary
    n = number of base units in one kaleidoscope image
    '''

    outputs = []

    img = Image.open(imagePath)
    w, h = img.size
    s = w/n

    x = list(range(int(s/2), w - int(s/2), fineness))
    y = list(range(int(s/2), h - int(s/2), fineness))

    for j in y:
        for i in x:
            print(i, j)
            square = img.crop((0+i, 0+j, s+i, s+j))
            output = kaleidoscope(square, mode, dispDim[0], dispDim[1], n)
            outputs.append(output)
    return outputs

def preprocess(image_name: str,
               x: int, y: int, width: int, height: int) -> Image.Image:
    img = Image.open(image_name)

    offset_factor = math.sqrt(x*x + y*y) / \
        math.sqrt(width*width + height*height)
    print(offset_factor)
    # calculate total normalized offset (between 0 and 1)
    # to apply transformation

    overshoot = abs(img.size[1] - img.size[0])
    if img.size[0] < img.size[1]:
        # image is taller than width
        s = img.size[0]
        return img.crop((0, overshoot * offset_factor,
                         s, s + overshoot * offset_factor))
    else:
        s = img.size[1]
        return img.crop((overshoot * offset_factor, 0,
                         s + overshoot * offset_factor, s))