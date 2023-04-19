# Imports for the entire notebook
import cv2
import math
import numpy as np
import pandas as pd
import pytesseract
import re
from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt

def remove_horizontal(x, y, i, img, mode="open"):
  """
  Find horizontal lines in given image
  """

  mode = mode.lower()

  if mode == "open":
    mode = cv2.MORPH_OPEN
  elif mode == "close":
    mode = cv2.MORPH_CLOSE
  else:
    raise Exception("Unsupported morpholocial transformation mode")

  horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (x,y))
  remove_horizontal = cv2.morphologyEx(img, mode, horizontal_kernel, iterations=i)

  return remove_horizontal

def remove_vertical(x, y, i, img, mode="open"):
  """
  Find vertical lines in given image
  """
  img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
  remove_vertical = remove_horizontal(x, y, i, img, mode)
  remove_vertical = cv2.rotate(remove_vertical, cv2.ROTATE_90_COUNTERCLOCKWISE)
  return remove_vertical

def remove_lines(orig, showOrig=True):
  """
  Removes vertical and horizontal lines from image
  """
  img = orig.copy()

  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  img_bin = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 5)

  img_height, img_width = img_bin.shape

  # inverting the image
  img_bin = 255 - img_bin

  kernel_len_ver = img_height // 50
  kernel_len_hor = img_width // 50

  ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len_ver))
  hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len_hor, 1))
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

  # Use horizontal kernel to detect and save the horizontal lines in a jpg
  image_1 = cv2.erode(img_bin, hor_kernel, iterations=3)
  no_horizontal = cv2.dilate(image_1, hor_kernel, iterations=4)
  no_horizontal2 = remove_horizontal(30, 1, 2, no_horizontal, "close")
  no_horizontal3 = remove_horizontal(50, 1, 2, no_horizontal2, "close")

  # Use vertical kernel to detect and save the vertical lines in a jpg
  image_2 = cv2.erode(img_bin, ver_kernel, iterations=3)
  no_vertical = cv2.dilate(image_2, ver_kernel, iterations=4)
  no_vertical2 = remove_vertical(30, 1, 2, no_vertical, "close")
  no_vertical3 = remove_vertical(50, 1, 2, no_vertical2, "close")

  #combining mask
  # mask = cv2.addWeighted(no_vertical3, 1, no_horizontal3, 1, 0.0)
  mask = cv2.bitwise_or(no_horizontal3, no_vertical3)

  # Eroding and thesholding the image
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
  mask = cv2.dilate(mask, kernel, iterations=1)

  orig[mask==255]=255

  return orig if showOrig == True else mask

def removedLinesCOMBO2(orig, showOrig=True):
  
  img = orig.copy()

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(gray, (3, 3), 0)
  ret,thresh_value = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

  # Remove horizontal lines
  no_horizontal = remove_horizontal(25, 1, 2, thresh_value) #20 vs 25
  no_horizontal2 = remove_horizontal(30, 1, 2, no_horizontal, "close")
  no_horizontal3 = remove_horizontal(50, 1, 2, no_horizontal2, "close")

  # Remove vertical lines
  no_vertical = remove_vertical(20, 1, 2, thresh_value)
  no_vertical2 = remove_vertical(50, 1, 2, no_vertical, "close")
  no_vertical3 = remove_vertical(100, 1, 2, no_vertical2, "close")  

  ###################################################################
  img = orig.copy()

  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  img_bin = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 5)
  img_height, img_width = img_bin.shape

  # inverting the image
  img_bin = 255 - img_bin

  kernel_len_ver = img_height // 50
  kernel_len_hor = img_width // 50

  ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len_ver))
  hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len_hor, 1))

  # Use horizontal kernel to detect and save the horizontal lines in a jpg
  image_1 = cv2.erode(img_bin, hor_kernel, iterations=3)
  no_horizontalB = cv2.dilate(image_1, hor_kernel, iterations=4)
  no_horizontal2B = remove_horizontal(30, 1, 2, no_horizontalB, "close")
  no_horizontal3B = remove_horizontal(50, 1, 2, no_horizontal2B, "close")

  # Use vertical kernel to detect and save the vertical lines in a jpg
  image_2 = cv2.erode(img_bin, ver_kernel, iterations=3)
  no_verticalB = cv2.dilate(image_2, ver_kernel, iterations=4)
  no_vertical2B = remove_vertical(30, 1, 2, no_verticalB, "close")
  no_vertical3B = remove_vertical(50, 1, 2, no_vertical2B, "close")
  no_vertical3B = remove_vertical(100, 1, 2, no_vertical3B, "close")
  ###################################################################

  final_horizontal = cv2.bitwise_or(no_horizontal3, no_horizontal3B)
  final_vertical = cv2.bitwise_or(no_vertical3, no_vertical3B)
  final_vertical = remove_vertical(200, 1, 2, final_vertical, "close")

  mask = cv2.bitwise_or(final_horizontal, final_vertical)

  mask = 255-mask

  orig[mask==0]=255

  return orig if showOrig == True else mask

def countCols(shape, finalContours, orig, showImages = False):
  colImg = np.zeros(shape, dtype=np.uint8)
  colImg.fill(255)

  for cnt in finalContours:
    x,y,w,h = cv2.boundingRect(cnt)
    cv2.rectangle(colImg,(x+3,y),(x+w-3,y+h),(0, 0, 0), -1)

  colImg = cv2.cvtColor(colImg, cv2.COLOR_BGR2GRAY)
  resize = cv2.resize(colImg, (shape[1], 10))
  blur = cv2.GaussianBlur(resize, (3,3), 0)  
  ret,thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
  
  kWidth = 10#int(shape[0]/8)

  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kWidth, 2))
  erode = cv2.erode(thresh, kernel, iterations=2)
  
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
  dilate = cv2.dilate(erode, kernel, iterations=1)

  contours, hierarchy = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  return len(contours)

def AClustering(orig, contours, psm=13, oem=3, digits=False):
  xCoords = []
  coords = []

  for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    xCoords.append([x, 0])
    coords.append((x, y, w, h))
  
  # apply hierarchical agglomerative clustering to the coordinates
  clustering = AgglomerativeClustering(
    n_clusters=None,
    metric="manhattan",
    linkage="complete",
    distance_threshold=25.0)
    
  clustering.fit(xCoords)

  # initialize our list of sorted clusters
  sortedClusters = []

  # loop over all clusters
  for l in np.unique(clustering.labels_):
    # extract the indexes for the coordinates belonging to the
    # current cluster
    idxs = np.where(clustering.labels_ == l)[0]
    # verify that the cluster is sufficiently large
    if len(idxs) > 2:
      # compute the average x-coordinate value of the cluster and
      # update our clusters list with the current label and the
      # average x-coordinate
      avg = np.average([coords[i][0] for i in idxs])
      sortedClusters.append((l, avg))
  # sort the clusters by their average x-coordinate and initialize our
  # data frame
  sortedClusters.sort(key=lambda x: x[1])
  df = pd.DataFrame()

  numRows = 0
  tokens = []
  tokenCoords = []
  tableCoords = []

  # loop over the clusters again, this time in sorted order
  # for (l, _) in sortedClusters:
  for j in range(len(sortedClusters)):
    l = sortedClusters[j][0]
    # extract the indexes for the coordinates belonging to the
    # current cluster
    idxs = np.where(clustering.labels_ == l)[0]
    # extract the y-coordinates from the elements in the current
    # cluster, then sort them from top-to-bottom
    yCoords = [coords[i][1] for i in idxs]
    sortedIdxs = idxs[np.argsort(yCoords)]
    # generate a random color for the cluster
    color = np.random.randint(0, 255, size=(3,), dtype="int")
    color = [int(c) for c in color]

    # loop over the sorted indexes
    im_list = []
    tokenCoords.append([])
    tableCoords.append([])
    for i in sortedIdxs:
      # extract the text bounding box coordinates and draw the
      # bounding box surrounding the current element

      (x,y,w,h) = coords[i]
      # cv2.rectangle(orig, (x, y), (x + w, y + h), color, 2)

      # stitch images, do convert here
      newImg = orig[y:y+h, x:x+w]
      im_list.append(newImg)
      tokenCoords[j].append((x,y,w,h))
      tableCoords[j].append((i, j))

    #get row count by counting max number of boxes:
    numRows = max(numRows, len(im_list))

    concat = hconcat_resize_max(im_list)
    # concat = vconcat_resize_max(im_list)
    ocr = convert(concat, psm, oem, digits)
    temp = re.split(r"\s|\n", ocr)
    temp = list(filter(None, temp))
    tokens.append(temp)
    
  numCols = len(sortedClusters)
  return numRows, numCols, tokens, tokenCoords, tableCoords

def AClusteringY(orig, contours, numRows):
  yCoords = []
  coords = []

  for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    yCoords.append([y, 0])
    coords.append((x, y, w, h))
  
  # apply hierarchical agglomerative clustering to the coordinates
  # clustering = AgglomerativeClustering(
  #   n_clusters=None,
  #   metric="manhattan",
  #   linkage="complete",
  #   distance_threshold=20.0)
  
  clustering = AgglomerativeClustering(
    n_clusters=numRows,
    metric="euclidean",
    linkage="ward")
    
  clustering.fit(yCoords)

  # clustering = AgglomerativeClustering().fit(xCoords)

  # initialize our list of sorted clusters
  sortedClusters = []

  # loop over all clusters
  for l in np.unique(clustering.labels_):
    # extract the indexes for the coordinates belonging to the
    # current cluster
    idxs = np.where(clustering.labels_ == l)[0]
    # verify that the cluster is sufficiently large
    if len(idxs) > 2:
      # compute the average x-coordinate value of the cluster and
      # update our clusters list with the current label and the
      # average x-coordinate
      avg = np.average([coords[i][0] for i in idxs])
      sortedClusters.append((l, avg))
  # sort the clusters by their average x-coordinate and initialize our
  # data frame
  sortedClusters.sort(key=lambda x: x[1])
  df = pd.DataFrame()

  # loop over the clusters again, this time in sorted order
  for (l, _) in sortedClusters:
    # extract the indexes for the coordinates belonging to the
    # current cluster
    idxs = np.where(clustering.labels_ == l)[0]
    # extract the y-coordinates from the elements in the current
    # cluster, then sort them from top-to-bottom
    xCoords = [coords[i][2] for i in idxs]
    sortedIdxs = idxs[np.argsort(xCoords)]
    # generate a random color for the cluster
    color = np.random.randint(0, 255, size=(3,), dtype="int")
    color = [int(c) for c in color]

    # loop over the sorted indexes
    for i in sortedIdxs:
      # extract the text bounding box coordinates and draw the
      # bounding box surrounding the current element

      (x,y,w,h) = coords[i]
      cv2.rectangle(orig, (x, y), (x + w, y + h), color, 2)
  
def find_text(orig, psm=13, oem=3, digits=False):

  img = orig.copy()

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(gray, (3,3), 0)
  ret,thresh_value = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
  erode = cv2.erode(thresh_value, kernel, iterations=1)    
  horizontal = 6 #img.shape[1] // 50

  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal, 2))
  dilate = cv2.dilate(erode, kernel, iterations=2)

  invert = 255 - dilate

  #do we really need all this now ?
  contours, hierarchy = cv2.findContours(invert, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  area = img.shape[0] * img.shape[1]

  height = orig.shape[0]
  width = orig.shape[1]
  area = height * width

  finalContours = []

  for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    if ((h * w) / area) < 0.000165 or ((h * w) / area) > 0.5:
      continue
    finalContours.append(cnt)

  ##################

  num_rows, num_cols, tokens, tokenCoords, tableCoords = AClustering(orig.copy(), finalContours, psm, oem, digits)
  AClusteringY(orig.copy(), finalContours, num_rows)

  mat = np.empty((num_rows, num_cols), dtype=np.dtype('U100'))

  for i in range(len(tokenCoords)):
      for j in range(len(tokenCoords[i])):

        (x,y,w,h) = tokenCoords[i][j]
        (tx, ty) = tableCoords[i][j]

        midx = x + (w/2)
        midy = y + (h/2)
        relx = midx / img.shape[1]
        rely = midy / img.shape[0]
        desx = math.floor(relx * num_cols)
        desy = math.floor(rely * num_rows)

        try:
          mat[desy][desx] = tokens[i][j]
        except IndexError:
          pass

  return orig, mat

def hconcat_resize_max(im_list, interpolation=cv2.INTER_CUBIC):
    h_max = max(im.shape[0] for im in im_list)

    new_list = []
    for im in im_list:
      dif = h_max - im.shape[0]

      top = (dif // 2) + 10
      bottom = dif - top + 10

      im2 = cv2.copyMakeBorder(im, top, bottom, 10, 10, cv2.BORDER_CONSTANT, None, value = [255, 255, 255])
      new_list.append(im2)

    return cv2.hconcat(new_list)

def convert(img, psm=6, oem=3, digits=False):
  """
  Returns the string contained in the image
  Uses pytesseract OCR to extract string from image
  """
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
  opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel, iterations=1)
  gray = cv2.resize(gray, (0,0), fx=2, fy=3)

  config = '--psm ' + str(psm) +  "--oem " + str(oem)

  if digits == True:
    config = config + ' -c tessedit_char_whitelist=0123456789 ,'

  ext = pytesseract.image_to_string(gray, config=config + " -c preserve_interword_spaces=1 -c digit_or_numeric_punct=0", lang='eng')

  return ext

def extract(IMAGE_PATH):

  pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

  image = cv2.imread(IMAGE_PATH)
  removed_lines = remove_lines(image)
  # removed_lines = removedLinesCOMBO2(image)
    
  bounded, mat = find_text(removed_lines, 11, 1)
  
#   DF = pd.DataFrame(mat)
#   DF.to_csv("mat.csv")
  
  return bounded, mat