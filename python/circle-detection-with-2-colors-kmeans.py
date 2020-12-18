import numpy as np
import cv2 as cv
import util

def main():
  util.setWindowName("Circle detection | OpenCV Demo")
  process()

def process():
  # Get a video stream from the webcam.
  # Play around with this for the correct number,
  # if you only have one webcam, it will be 0.
  input = util.openInput(1)

  # Loop for processing the frames.
  while True:
    begin = util.millis()
    grabbed, frame = input.read()

    # Check if we have a valid frame.
    if not grabbed:
      print("Can't receive frame, exiting..")
      break

    # Prepare the frame.
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray = cv.pyrDown(gray)
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
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, 35, param1=150, param2=25, minRadius=5, maxRadius=45)

    # Draw the circles.
    if not circles is None:
      # Get the circles.
      circles = getCircles(circles, util.getRatio(frame, gray))
      # Get the first color.
      for circle in circles:
        circle["colors"] = getCircleColors(frame, circle)
      # Draw the circles.
      drawCircles(frame, circles)
    
    # Draw the FPS.
    util.drawFPS(frame, duration)

    # Show the frame.
    if not util.show(frame):
      break

  # Cleanup.
  input.release()
  cv.destroyAllWindows()

def getCircles(circles, ratio):
  # Format and round the detected circles so we can loop.
  circles = np.uint16(np.around(circles))
  foundCircles = []

  for circle in circles[0, :]:
    # Get the postion and dimension.
    x = circle[0] * ratio
    y = circle[1] * ratio
    radius = circle[2] * ratio

    foundCircles.append({ "x": x, "y": y, "radius": radius, "colors": [] })

  return foundCircles

def getCircleColors(frame, circle):
  # Create a mask the same size as our frame and fill it with zeros (black).
  mask = np.zeros(frame.shape, np.uint8)
  # Draw our circle in white on the mask.
  cv.circle(mask, (circle["x"], circle["y"]), circle["radius"], (255, 255, 255, 255), -1)
  # Mask the frame.
  roi = cv.bitwise_and(frame, mask)
  # Reshape all pixels to be in a single array.
  roi = roi.reshape((-1, 3))
  # Remove all pixels that are totally black.
  roi = roi[~np.all(roi == 0, axis=1)]
  # Convert to float.
  roi = np.float32(roi)
  # Define the criteria and get the kmeans.
  criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 1, 1.0)
  ret, label, center = cv.kmeans(roi, 2, None, criteria, 1, cv.KMEANS_PP_CENTERS)
  
  # Return the found colors as a list of BGR integers.
  return list(map(lambda color: [round(color[0]), round(color[1]), round(color[2])], center))


## DRAWING
def drawCircles(frame, circles):
  for circle in circles:
    # Draw the first color on the frame.
    cv.ellipse(frame, (circle["x"], circle["y"]), (circle["radius"], circle["radius"]), 0, 90, 270, circle["colors"][0], 4)
    # Draw the second color on the frame.
    cv.ellipse(frame, (circle["x"], circle["y"]), (circle["radius"], circle["radius"]), 0, 270, 450, circle["colors"][1], 4)


# Run the main function if the file is run as a script.
if __name__ == "__main__":
  main()
