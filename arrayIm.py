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

def mask(img: np.array , bounds: list) -> np.array:
  '''
  masks img as shape defined by bounds
  '''
  pts = np.array(bounds)

  ## (1) Crop the bounding rect
  x, y = np.min(pts, axis = 0)
  w, h = np.max(pts, axis = 0)
  cropped = img[y:h, x:w]

  ## (2) make mask
  mask = np.zeros(cropped.shape[0:2], np.uint8)
  cv2.fillPoly(mask, [pts], (255,255,255))

  ## (3) do bit-op
  dst = cv2.bitwise_and(cropped, cropped, mask=mask)
  cv2_imshow(dst)