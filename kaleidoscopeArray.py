import math
from arrayIm import *
from scipy import ndimage
from PIL import Image, ImageDraw, ImageOps
# Enumerations
EQUILATERAL = 0
RIGHT_SCALENE = 1
RIGHT_SQUARE = 2
RIGHT_DIAMOND = 3

rotate = ndimage.rotate

def make_triangle(img: Image.Image, mode: int = EQUILATERAL) -> Image.Image:
    '''
    Produces triangular crop of image from a square image
    '''
    s: int = img.shape[0]

    if mode == EQUILATERAL:
        # equilateral triangle with base at left side of image
        vertices = [[0, 0], [0, s], [int(s*math.sin(math.pi/3)), int(s/2)]]
    elif mode == RIGHT_SCALENE:
        # right triangle with angles 30-60-90
        vertices = [[0, 0], [0, int(s*math.tan(math.pi/6))], [s, 0]]
    elif mode == RIGHT_SQUARE or mode == RIGHT_DIAMOND:
        # isoceles right triangle
        vertices = [[0, 0], [0, s], [s, 0]]

    # make triangular mask
    triangle = maskIm(img, vertices)
    
    return triangle


def reflect_triangle(triangle: Image.Image) -> Image.Image:
    '''
    Returns triangle reflected.
    '''
    h, w, _ = triangle.shape
    output = makeIm((h*2, w))
    output = pasteIm(output, triangle, (h, 0))
    mirror = cv2.flip(triangle, 0)
    output = pasteIm(output, mirror, (0, 0))
    return output


def make_trapezoid(triangle: Image.Image, mode: int = 0) -> Image.Image:
    '''
    Creates a trapezoid out of 3 triangles.
    '''
    if mode == RIGHT_SCALENE:
        triangle = reflect_triangle(triangle)

    h, w, _ = triangle.shape
    output = makeIm((h*2-5, w))

    # paste original triangle in top left corner of new canvas
    output = pasteIm(output, triangle, (0, 0))

    # mirror, rotate, crop to size, and paste below first triangle
    mirror = cv2.flip(triangle, 0)
    rotated = rotate(mirror, 60, reshape = True, order=0)
    rotated = cropIm(rotated, (0, rotated.shape[0]-h, w, rotated.shape[1]))
    output = pasteIm(output, rotated, (int(h/2), 0))

    # add a 2 pixel offset to get rid of
    # white gap between bottom and middle triangles
    rotated = rotate(triangle, 240, reshape=True, order=0)
    rotated = cropIm(rotated, (rotated.shape[1]-w, 0, rotated.shape[1], h))
    output = pasteIm(output, rotated, (h-2, 0))

    return output

def make_unit(triangle: Image.Image, mode: int = EQUILATERAL) -> Image.Image:

    if mode == EQUILATERAL or mode == RIGHT_SCALENE:
        #make trapezoid first
        triangle = make_trapezoid(triangle, mode)
        h, w, _ = triangle.shape

        output = makeIm((h, w*2))
        output = pasteIm(output, triangle, (0, int(w)))
        flip = cv2.flip(triangle, 1)
        output = pasteIm(output, flip, (0,0))
    
    else:
        triangle = reflect_triangle(triangle)
        h, w, _ = triangle.shape
        
        output = makeIm((h, w*2))
        output = pasteIm(output, triangle, (0,0))
        flip = cv2.flip(triangle, 1)
        output = pasteIm(output, flip, (0, w))

        rotated = rotate(triangle, 90, reshape=True, order = 0)
        output = pasteIm(output, rotated, (int(h/2), 0))
        flip = cv2.flip(rotated, 0)
        output = pasteIm(output, flip, (0,0))

        if mode == RIGHT_DIAMOND:
            output = rotate(output, 45, reshape=True, order = 0)
            output = cropIm(output, (2, 2, output.shape[1], output.shape[0]))
    
    return output

def tessellate(img: Image.Image, dim: tuple = (1080, 1920),
               n: int = 5, mode: int = 0) -> Image.Image:
    '''
    dim = dimensions of final image as (height, width)
    n = number of horizontal repetitions
    '''
    output = makeIm(dim)

    y, x = dim
    b, a, _ = img.shape
    ratio = (x/n)/a

    w = int(a*ratio)
    h = int(b*ratio)
    img = cv2.resize(img, (w, h))

    if mode == EQUILATERAL or mode == RIGHT_SCALENE:
        for j in range(-1, int(y/h)+2):
            # use 2 options to offset the pattern
            # start at -1 so left and upper edges are filled
            if not j % 2:
                # TODO: Can we make this more efficient (i.e. not %2, by doing step = 2)
                for i in range(int(x/w)+2):
                    #output.paste(img, (w*i, (int(h*3/4))*j), img)
                    output = pasteIm(output, img, ((int(h*3/4))*j, w*i))
            elif j % 2:
                for i in range(-1, int(x/w)+2):
                    output = pasteIm(output, img, ((int(h*3/4))*j, int(w/2)+i*w))
                    #output.paste(img, (int(w/2)+i*w, (int(h*3/4))*j), img)

    elif mode == RIGHT_SQUARE:
        for j in range(int(y/w)+2):
            for i in range(int(x/h)):
                output = pasteIm(output, img, (h*j, w*i))  

    elif mode == RIGHT_DIAMOND: 
        for j in range(-1, int(y/h)+4):
            if not j % 2:
                for i in range(int(x/w)+2):
                    output = pasteIm(output, img, (int(h/2)*j, w*i))
            elif j % 2:
                for i in range(-1, int(x/w)+2):
                    output = pasteIm(output, img, (int(h/2)*j, int(w/2)+i*w))

    return output

def kaleidoscope(img: Image.Image, mode=EQUILATERAL,
                 windowX: int = 1920, windowY: int = 1080) -> Image.Image:
    '''
    mode = 0 (equilateral)
           1 (right-scalene)
           2 (right-isoceles, square)
           3 (right-isoceles, diamond)
    '''
    triangle = make_triangle(img, mode)
    unit = make_unit(triangle, mode)

    return tessellate(unit, img.size[0], (windowX, windowY), 5, mode)


def preprocess(image_name: str,
               x: int, y: int, width: int, height: int) -> Image.Image:
    img = cv2.imread(image_name)

    offset_factor = math.sqrt(x*x + y*y) / \
        math.sqrt(width*width + height*height)
    print(offset_factor)
    # calculate total normalized offset (between 0 and 1)
    # to apply transformation

    overshoot = abs(img.shape[1] - img.shape[0])
    if img.shape[1] < img.shape[0]:
        # image is taller than width
        s = img.shape[1]
        return img.crop((0, overshoot * offset_factor,
                         s, s + overshoot * offset_factor))
    else:
        s = img.shape[0]
        return img.crop((overshoot * offset_factor, 0,
                         s + overshoot * offset_factor, s))