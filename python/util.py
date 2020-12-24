import time
import cv2 as cv

WINDOW_NAME = "OpenCV Demo"


## GENERAL
def millis() -> int:
  return int(time.time_ns() / 1000000)

def getRatio(img1, img2, shouldRound = True):
  if shouldRound:
    return round(img1.shape[1] / img2.shape[1])
  else:
    return img1.shape[1] / img2.shape[2]

def resize(src, percentage):
  # Resize the given source to the given percentage.
  return cv.resize(src, (0, 0), None, percentage / 100, percentage / 100)

def inRange(val1: int, val2: int, range: int) -> bool:
  return val1 + range >= val2 and val1 - range <= val2

# INPUT
def openInput(input, props=[]):
  input = cv.VideoCapture(input)

  for prop in props:
    input.set(prop[0], prop[1])

  if not input.isOpened():
    errorAndExit("Cannot open camera")

  return input


## OUTPUT
def setWindowName(name: str):
  global WINDOW_NAME
  WINDOW_NAME = name
  cv.namedWindow(WINDOW_NAME)

def drawTitle(frame, title):
  cv.putText(frame, title, (60, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv.LINE_AA)

def drawFPS(frame, duration: int):
  fps = str(round(1000 / duration))
  cv.putText(frame, fps, (frame.shape[1] - 60, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv.LINE_AA)

def show(img, delay: int = 1) -> bool:
  cv.imshow(WINDOW_NAME, img)

  # Return false if Q is pressed.
  if cv.waitKey(delay) == ord("q"):
    return False
  # Return false if the window is closed.
  if cv.getWindowProperty(WINDOW_NAME, cv.WND_PROP_VISIBLE) == 0:
    return False

  return True


## ERRORS
def errorAndExit(message: str):
  print(message)
  exit()