import math
from arrayIm import *
from scipy import ndimage

# Enumerations
EQUILATERAL = 0
RIGHT_SCALENE = 1
RIGHT_SQUARE = 2
RIGHT_DIAMOND = 3

rotate = ndimage.rotate

def make_triangle(img: np.array, mode: int = EQUILATERAL) -> np.array:
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


def reflect_triangle(triangle: np.array) -> np.array:
    '''
    Returns triangle reflected.
    '''
    h, w, _ = triangle.shape
    output = makeIm((h*2, w))
    output = pasteIm(output, triangle, (h, 0))
    mirror = cv2.flip(triangle, 0)
    output = pasteIm(output, mirror, (0, 0))
    return output


def make_trapezoid(triangle: np.array, mode: int = 0) -> np.array:
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

def make_unit(triangle: np.array, mode: int = EQUILATERAL) -> np.array:

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

def tessellate(img: np.array, dim: tuple = (1080, 1920),
               n: int = 5, mode: int = 0) -> np.array:
    '''
    dim = dimensions of final image as (height, width)
    n = number of horizontal repetitions
    '''
    y, x = dim
    b, a, _ = img.shape
    ratio = (x/n)/a

    h = int(b*ratio)
    w = int(a*ratio)
    img = cv2.resize(img, (w, h))

    if mode == 0 or mode == 1:
        base = makeIm((int(h*6/4)-1, w))
        row2 = np.tile(img, (2,1))
        base = pasteIm(base, img, (0,0))
        base = pasteIm(base, row2, (-int(h*3/4), -int(w/2)))

    elif mode == 2:
        base = img

    elif mode == 3:
        base = img
        base = paste(base, img, (-int(h/2), -int(w/2)))

    #repeat the base unit, and crop to fit dimensions
    output = np.tile(base, (math.ceil(y/h),n,1))
    output = cropIm(output, (0, 0, x, y))

    return output

def kaleidoscope(img: np.array, mode=EQUILATERAL,
                 windowY: int = 1080, windowX: int = 1920) -> np.array:
    '''
    mode = 0 (equilateral)
           1 (right-scalene)
           2 (right-isoceles, square)
           3 (right-isoceles, diamond)
    '''
    triangle = make_triangle(img, mode)
    unit = make_unit(triangle, mode)

    return tessellate(unit, (windowY, windowX), 5, mode)


def preprocess(image_name: str,
               x: int, y: int, width: int, height: int) -> np.array:
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

