from kaleidoscope import kaleidoscope
from PIL import Image

def gen_images(imagePath: str, dispDim: tuple = (1920, 1080),
               mode = 0, fineness: int = 50, n: int = 4) -> list:
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
        outputs.append([])

        for i in x:
            print(i, j)
            square = img.crop((0+i, 0+j, s+i, s+j))
            output = kaleidoscope(square, mode, dispDim[0], dispDim[1], n)
            outputs[-1].append(output)
    return outputs
