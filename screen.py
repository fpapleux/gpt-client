import sys, pyautogui, time, json
from screeninfo import get_monitors
from io import BytesIO
import numpy as np
import cv2
import imutils


object_name = "Microsoft Word Icon"
screen_height = 0
screen_width = 0
screenshot_height = 0
screenshot_width = 0

# establish current monitor dimensions
for m in get_monitors():
    if m.is_primary:
        screen_height = m.height
        screen_width = m.width
print (f"computer screen resolution: width = {screen_width}, height = {screen_height}")


def method1():
    # Grab screenshot
    img = pyautogui.screenshot()
    print (f"screenshot dimensions: width = {img.width}, height = {img.height}")
    img.show()
    return

def method2():
    img = pyautogui.screenshot()
    imgcv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    imutils.resize(imgcv, width=screen_width)
    #imutils.resize(img, width=screen_width)
    newimg = img.resize((screen_width, screen_height))

    print (f"screenshot dimensions: width = {newimg.width}, height = {newimg.height}")
    newimg.show()
    #cv2.imwrite("in_memory_to_disk.png", img)
    return

method2()

