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

# INPUT
def openInput(input):
  input = cv.VideoCapture(input)

  if not input.isOpened():
    errorAndExit("Cannot open camera")

  return input


## OUTPUT
def setWindowName(name: str):
  global WINDOW_NAME
  WINDOW_NAME = name

def drawFPS(frame, duration: int):
  fps = str(round(1000 / duration))
  cv.putText(frame, fps, (frame.shape[1] - 60, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv.LINE_AA)

def show(img) -> bool:
  cv.imshow(WINDOW_NAME, img)

  # Return false if Q is pressed.
  if cv.waitKey(1) == ord("q"):
    return False
  # Return false if the window is closed.
  if cv.getWindowProperty(WINDOW_NAME, cv.WND_PROP_VISIBLE) == 0:
    return False

  return True


## ERRORS
def errorAndExit(message: str):
  print(message)
  exit()