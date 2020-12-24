import numpy as np
import cv2 as cv
import collections
import util

# Dictionary for the HSV mask sliders.
HSV = {
  "lowH": 0,
  "highH": 180,
  "lowS": 0,
  "highS": 70,
  "lowV": 45,
  "highV": 160
}

# Dictionary for the HoughCircles detection sliders.
CIRCLE = {
  "dp": 10,
  "minDist": 25,
  "highThresh": 140,
  "accThresh": 14,
  "minRadius": 12,
  "maxRadius": 16
}

# Size limited collection for the circle buffer.
detectedCircles = collections.deque(maxlen=15)

def main():
  util.setWindowName("Pool ball detection | OpenCV Demo")

  # Create sliders for the HSV values.
  cv.createTrackbar("lowH", util.WINDOW_NAME, HSV["lowH"], 180, lambda val: onHSVTrackbar("lowH", val))
  cv.createTrackbar("highH", util.WINDOW_NAME, HSV["highH"], 180, lambda val: onHSVTrackbar("highH", val))
  cv.createTrackbar("lowS", util.WINDOW_NAME, HSV["lowS"], 255, lambda val: onHSVTrackbar("lowS", val))
  cv.createTrackbar("highS", util.WINDOW_NAME, HSV["highS"], 255, lambda val: onHSVTrackbar("highS", val))
  cv.createTrackbar("lowV", util.WINDOW_NAME, HSV["lowV"], 255, lambda val: onHSVTrackbar("lowV", val))
  cv.createTrackbar("highV", util.WINDOW_NAME, HSV["highV"], 255, lambda val: onHSVTrackbar("highV", val))
  # Create sliders for the circle detection values.
  cv.createTrackbar("dp", util.WINDOW_NAME, CIRCLE["dp"], 30, lambda val: onCircleTrackbar("dp", val))
  cv.createTrackbar("minDist", util.WINDOW_NAME, CIRCLE["minDist"], 150, lambda val: onCircleTrackbar("minDist", val))
  cv.createTrackbar("highTresh", util.WINDOW_NAME, CIRCLE["highThresh"], 255, lambda val: onCircleTrackbar("highThresh", val))
  cv.createTrackbar("accThresh", util.WINDOW_NAME, CIRCLE["accThresh"], 255, lambda val: onCircleTrackbar("accThresh", val))
  cv.createTrackbar("minRadius", util.WINDOW_NAME, CIRCLE["minRadius"], 100, lambda val: onCircleTrackbar("minRadius", val))
  cv.createTrackbar("maxRadius", util.WINDOW_NAME, CIRCLE["maxRadius"], 100, lambda val: onCircleTrackbar("maxRadius", val))

  # Start processing.
  process()

# Update a HSV value when a slider is moved.
def onHSVTrackbar(name, value):
  HSV[name] = value

# Update a circle detection value when a slider is moved.
def onCircleTrackbar(name, value):
  CIRCLE[name] = value

def process():
  # Get a video stream from the webcam.
  # Play around with this for the correct number,
  # if you only have one webcam, it will be 0.
  input = util.openInput(0)
  # input = util.openInput("../potje-pool.mp4")

  # Loop for processing the frames.
  while True:
    begin = util.millis()
    grabbed, frame = input.read()

    # Check if we have a valid frame.
    if not grabbed:
      print("Can't receive frame, exiting..")
      break
    
    # Prepare the frame.
    frame = frame[70:frame.shape[0] - 70, 70:frame.shape[1] - 70]
    # gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # gray = cv.pyrDown(gray)
    # gray = cv.medianBlur(gray, 5)
    # thresh, gray = cv.threshold(gray, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
    # gray = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_MASK, 11, 5)

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    hsvMask = cv.inRange(hsv, (HSV["lowH"], HSV["lowS"], HSV["lowV"]), (HSV["highH"], HSV["highS"], HSV["highV"]))

    hsvMask = cv.bitwise_not(hsvMask)
    maskedFrame = cv.bitwise_and(frame, frame, mask = hsvMask)
    gray = cv.cvtColor(maskedFrame, cv.COLOR_BGR2GRAY)
    gray = cv.medianBlur(gray, 5)

    # Detect circles using HoughCircles.
    # Params:
    # 1: The input image.
    # 2: The type of detection, only HOUGH_GRADIENT is supported.
    # 3: dp - Inverse ratio of the accumulator resolution to the image resolution, 1 = same as input, 2 = half the input.
    # 4: minDist - Minimum distance between the centers of the circles.
    # 5 (param1): highThreshold - High threshold for the Canny edge detector (low is half).
    # 6 (param2): accumulatorThreshold - Accumulator threshold for the circle centers, smaller means more false circle may be detected.
    #             Circles with the largest accumulator will be returned first.
    # 7 (minRadius): Minimum circle radius.
    # 8 (maxRadius): Maximum cirlce radius.
    # circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, 20, param1=100, param2=14, minRadius=14, maxRadius=14)
    # circles = cv.HoughCircles(hsvMask, cv.HOUGH_GRADIENT, 1, 25, param1=50, param2=14, minRadius=14, maxRadius=16)
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, CIRCLE["dp"] / 10, CIRCLE["minDist"], param1=CIRCLE["highThresh"], param2=CIRCLE["accThresh"], minRadius=CIRCLE["minRadius"], maxRadius=CIRCLE["maxRadius"])
    detectedCircles.append(getDetectedCircles(circles, util.getRatio(frame, gray)))

    # Form a 2 color mask.
    thresh, mask = cv.threshold(frame, 160, 255, cv.THRESH_BINARY)
    mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
    thresh, mask = cv.threshold(mask, 230, 255, cv.THRESH_BINARY)

    circles = getCircles()

    # Draw the circles.
    if len(circles) > 0:
      # Get the first color.
      for circle in circles:
        circle["colors"].append(getCircleColor(frame, mask, circle))
      # Invert the mask.
      mask = cv.bitwise_not(mask)
      # Get the second color.
      for circle in circles:
        circle["colors"].append(getCircleColor(frame, mask, circle))
      # Draw the circles.
      drawCircles(frame, circles)
    
    # Draw the FPS.
    util.drawFPS(frame, util.millis() - begin)

    # Convert the grayscale images to color
    hsvMask = cv.cvtColor(hsvMask, cv.COLOR_GRAY2BGR)
    mask = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)

    # Show the frame.
    util.drawTitle(frame, "Output")
    util.drawTitle(maskedFrame, "Masked frame")
    util.drawTitle(hsvMask, "Frame mask")
    util.drawTitle(mask, "Color mask")
    image = createImage(frame, maskedFrame, hsvMask, mask)
    if not util.show(image):
      break

  # Cleanup.
  input.release()
  cv.destroyAllWindows()

# Transform the detected circles using HoughCircles into an array of x, y and radius tuples.
def getDetectedCircles(circles, ratio):
  if circles is None: return []
  # Format and round the detected circles so we can loop.
  circles = np.uint16(np.around(circles))
  detectedCircles = []

  for circle in circles[0, :]:
    # Get the postion and dimension.
    x = circle[0] * ratio
    y = circle[1] * ratio
    radius = circle[2] * ratio

    detectedCircles.append((x, y, radius))

  return detectedCircles

# Get the detected circles based on the values in the circle buffer.
def getCircles():
  if len(detectedCircles) != detectedCircles.maxlen: return []
  groupedCircles = []
  circles = []

  # Group circles that are within a few pixels of each other.
  for circle in detectedCircles:
    for c in circle:
      existingCircle = next((x for x in groupedCircles if util.inRange(x[0][0], c[0], 10) & util.inRange(x[0][1], c[1], 6)), None)

      if existingCircle is None:
        groupedCircles.append([c])
      else:
        existingCircle.append(c)

  # Get the average of the group and build the circle for drawing.
  for group in groupedCircles:
    if len(group) != detectedCircles.maxlen: continue
    mean = np.mean(group, 0, np.integer)

    circles.append({ "x": mean[0], "y": mean[1], "radius": mean[2], "colors": [] })

  return circles

def getCircleColor(frame, frameMask, circle):
  # Create a mask the same size as our frame and fill it with zeros (black).
  mask = np.zeros(frame.shape[:2], np.uint8)
  # Draw our circle in white on the mask.
  cv.circle(mask, (circle["x"], circle["y"]), circle["radius"], (255, 255, 255, 255), -1)
  # Merge the masks.
  mask = cv.bitwise_and(frameMask, mask)
  # Get the mean color of the masked circle
  mean = cv.mean(frame, mask)
  
  # Return the BGR values as integer.
  return (round(mean[0]), round(mean[1]), round(mean[2]))


## DRAWING
def drawCircles(frame, circles):
  for circle in circles:
    # Draw white circle.
    # cv.circle(frame, (circle["x"], circle["y"]), circle["radius"], (255, 255, 255), 2)
    # Draw the first color on the frame.
    cv.ellipse(frame, (circle["x"], circle["y"]), (circle["radius"] + 8, circle["radius"] + 8), 0, 90, 270, circle["colors"][0], 4)
    # Draw the second color on the frame.
    cv.ellipse(frame, (circle["x"], circle["y"]), (circle["radius"] + 8, circle["radius"] + 8), 0, 270, 450, circle["colors"][1], 4)


## UTIL
def createImage(src1, src2, src3, src4):
  # Resize all sources to 60% of their original size.
  size = 60
  # Create the rows.
  row1 = np.hstack((util.resize(src1, size), util.resize(src2, size)))
  row2 = np.hstack((util.resize(src3, size), util.resize(src4, size)))
  return np.vstack((row1, row2))


# Run the main function if the file is run as a script.
if __name__ == "__main__":
  main()
