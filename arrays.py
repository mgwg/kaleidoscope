import numpy as np
import cv2

def pasteIm(paper: np.array, cutout: np.array, coord: tuple) -> np.array:
    '''
    alternative to Pillow's Image.paste() function using arrays
    paper = base image
    cutout = image to be pasted on
    coord = coordinate of base image where top left corner of cutout is to be placed
    '''
    w, h, _ = paper.shape
    a, b = coord

    # find opaque pixels in the image
    alpha = cutout[:,:,3]
    replace = np.where(alpha > 0)
    
    l = []
    for i in range(len(replace[0])):
      l.append((replace[0][i], replace[1][i]))
    
    # only paste the opaque pixels and do some math so everything is indexed within bounds
    for pixel in l:
      if pixel[0] + a < w and pixel[1] + b < h:
        paper[pixel[0]+a][pixel[1]+b]=cutout[pixel]

    #cv2.imshow(source)
    return paper