import numpy as np
import cv2

def jpg2png(jpg: np.array) -> np.array:
  '''
  adds alpha channel to an RGB image
  '''
  if jpg.shape[2] < 4:
    alphaChannel = np.empty((jpg.shape[0], jpg.shape[1],1))
    alphaChannel.fill('225')
    return np.concatenate((jpg, alphaChannel), axis = 2)
  else:
    return jpg

def makeIm(dim: tuple) -> np.array:
  '''
  makes a transparent RGBA image with dim = (width, height) dimensions
  '''
  blank_image = np.zeros((dim[0],dim[1],4), np.uint8)
  blank_image.fill(0)

  return blank_image

def cropIm(img: np.array, dim: tuple) -> np.array:
  '''
  img = image t be cropped
  dim = tuple containing the left, upper, right, and bottom boundaries of the crop
  '''
  return img[dim[1]:dim[3], dim[0]:dim[2]]

def pasteIm(paper: np.array, cutout: np.array, coord: tuple = (0,0)) -> np.array:
  '''
  alternative to Pillow's Image.paste() function using arrays
  paper = base image
  cutout = image to be pasted on
  coord = coordinate of base image where top left corner of cutout is to be placed as (y, x) becuase I made a booboo
  '''
  w, h, _ = paper.shape
  a, b = coord

  alpha = cutout[:,:,3]
  replace = np.where(alpha > 200) #==225

  # only want points where destination coordinate is within image points
  
  xCuts = np.where(replace[0] + a < w)
  yCuts = np.where(replace[1] + b < h)
  indices = np.intersect1d(xCuts, yCuts)
  
  x = replace[0][indices]
  y = replace[1][indices]
  destx = x + a
  desty = y + b

  paper[destx,desty] = cutout[x,y]
  
  return paper


def maskIm(img: np.array , bounds: list) -> np.array:
  '''
  masks img as shape defined by bounds
  '''
  pts = np.array(bounds)

  # crop img to be same size as mask
  x, y = np.min(pts, axis = 0)
  w, h = np.max(pts, axis = 0)
  cropped = img[y:h, x:w]

  # make mask
  mask = np.zeros(cropped.shape[0:2], np.uint8)
  cv2.fillPoly(mask, [pts], (255,255,255))

  # bit-op to make shape
  output = cv2.bitwise_and(cropped, cropped, mask=mask)
  return output
  