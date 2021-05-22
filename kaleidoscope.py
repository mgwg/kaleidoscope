from PIL import Image, ImageDraw, ImageOps
import math

# Enumerations
EQUILATERAL = 0
RIGHT_SCALENE = 1
RIGHT_SQUARE = 2
RIGHT_DIAMOND = 3


def make_triangle(img: Image.Image, mode: int = EQUILATERAL) -> Image.Image:
    '''
    Produces triangular crop of image from a square image
    '''
    s: int = img.size[0]

    if mode == EQUILATERAL:
        # equilateral triangle with base at left side of image
        vertices = [(0, 0), (0, s), (s*math.sin(math.pi/3), s/2)]
        # crop image to fit triangle
        triangle = Image.new(
            'RGBA', (int(s*math.sin(math.pi/3)), s), (255, 225, 225, 0))
    elif mode == RIGHT_SCALENE:
        # right triangle with angles 30-60-90
        vertices = [(0, 0), (0, s*math.tan(math.pi/6)), (s, 0)]
        triangle = Image.new(
            'RGBA', (s, int(s*math.tan(math.pi/6))), (255, 225, 225, 0))
    elif mode == RIGHT_SQUARE or mode == RIGHT_DIAMOND:
        # isoceles right triangle
        vertices = [(0, 0), (0, s), (s, 0)]
        triangle = Image.new('RGBA', (s, s), (255, 225, 225, 0))

    # make triangular mask
    mask: Image = Image.new('1', (s, s))
    draw = ImageDraw.Draw(mask)
    draw.polygon(vertices, fill='red')

    # make triangle
    triangle.paste(img, mask=mask)

    return triangle


def reflect_triangle(triangle: Image.Image) -> Image.Image:
    '''
    Returns triangle reflected.
    '''
    w, h = triangle.size
    output = Image.new(
        'RGBA', (w, h*2), color=(225, 225, 225, 0))
    output.paste(triangle, (0, h), mask=triangle)
    mirror = ImageOps.flip(triangle)
    output.paste(mirror, mask=mirror)
    return output


def make_trapezoid(triangle: Image.Image, mode: int) -> Image.Image:
    '''
    Creates a trapezoid out of 3 triangles.
    '''
    if mode == RIGHT_SCALENE:
        triangle = reflect_triangle(triangle)

    w, h = triangle.size
    output = Image.new('RGBA', (w, h*2-5), color=(225, 225, 225, 0))

    # paste original triangle in top left corner of new canvas
    output.paste(triangle, mask=triangle)

    # mirror, rotate, crop to size, and paste below first triangle
    mirror = ImageOps.flip(triangle)
    rotated = mirror.rotate(60, expand=True)
    rotated = rotated.crop((0, rotated.size[1]-h, w, rotated.size[1]))
    output.paste(rotated, box=(0, int(h/2)), mask=rotated)

    rotated = triangle.rotate(240, expand=True)
    # add a 2 pixel offset to get rid of
    # white gap between bottom and middle triangles
    rotated = rotated.crop((rotated.size[0]-w, 0, rotated.size[0], h))
    output.paste(rotated, box=(0, h-2), mask=rotated)

    return output


def make_unit(shape: Image.Image, mode: int = EQUILATERAL) -> Image.Image:

    if mode == EQUILATERAL or mode == RIGHT_SCALENE:
        shape = make_trapezoid(shape, mode)
        w, h = shape.size
        output = Image.new('RGBA', (w*2, h), color=(225, 225, 225, 0))

        output.paste(shape, (int(w), 0), shape)
        flip = ImageOps.mirror(shape)
        output.paste(flip, (0, 0), flip)

    else:
        shape = reflect_triangle(shape)
        w, h = shape.size
        output = Image.new('RGBA', (w*2, h), color=(225, 225, 225, 0))

        output.paste(shape, mask=shape)
        flip = ImageOps.mirror(shape)
        output.paste(flip, (w, 0), flip)

        rotated = shape.rotate(90, expand=True)
        output.paste(rotated, box=(0, int(h/2)), mask=rotated)
        flip = ImageOps.flip(rotated)
        output.paste(flip, mask=flip)

        if mode == RIGHT_DIAMOND:
            output = output.rotate(45, expand=True)
            output = output.crop((2, 2, output.size[0]-2, output.size[1]-2))

    return output


def tessellate(shape: Image.Image, mode: int = 0, dim: tuple = (1920, 1080),
               n: int = 5) -> Image.Image:
    '''
    dim = dimensions of final image
    n = number of horizontal repetitions
    s = side length of triangle in pixels
    '''
    output = Image.new('RGBA', dim, color=(255, 255, 255, 0))

    x, y = dim
    a, b = shape.size
    ratio = (x/n)/a

    w = int(a*ratio)
    h = int(b*ratio)
    shape = shape.resize((w, h))

    if mode == EQUILATERAL or mode == RIGHT_SCALENE:
        for j in range(-1, math.ceil(y/h)+1, 2):
            # start at -1 so left and upper edges are filled
            for i in range(-1, n+1):
                output.paste(shape, (int(w/2)+i*w, (int(h*3/4))*j), shape)
                output.paste(shape, ((w)*i, (int(h*3/4))*(j+1)), shape)

    elif mode == RIGHT_SQUARE:
        for j in range(math.ceil(y/h)+1):
            for i in range(n):
                output.paste(shape, (w*i, h*j), shape)

    elif mode == RIGHT_DIAMOND:
        for j in range(-1, math.ceil(y/h)+3, 2):
            for i in range(-1, n):
                output.paste(shape, (w*i, int(h/2)*(j+1)), shape)
                output.paste(shape, (int(w/2)+i*w, (int(h/2))*j), shape)

    return output


def kaleidoscope(img: Image.Image, mode=EQUILATERAL,
                 windowX: int = 600, windowY: int = 600) -> Image.Image:

    triangle = make_triangle(img, mode)
    unit = make_unit(triangle, mode)

    return tessellate(unit, (windowX, windowY), 5, mode)



