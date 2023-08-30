#Imports
import os
import pyautogui
from pynput import mouse
import pyscreeze
from time import sleep

#Global variables
CLICK1 = [0,0]
CLICK2 = [0,0]
CLICK3 = [0,0]
OKAY = [0,0]
COUNT = 0

def mouse_Location(x, y, button, pressed):
    global CLICK1
    global CLICK2
    global CLICK3
    global COUNT

    if pressed:
        COUNT += 1
        print(COUNT)
        if COUNT == 1:
            CLICK1 = [x,y]
        elif COUNT == 2:
            CLICK2 = [x,y]
        elif COUNT == 3:
            CLICK3 = [x,y]


    if COUNT == 3:
        print('Clicks confirmed.')
        COUNT = 0
        return False

def okay_Location(x, y, button, pressed):
    global OKAY
    global COUNT

    if pressed:
        COUNT += 1
        OKAY = [x,y]
        print('click 1')

    if COUNT == 1:
        return False



print('Click on three spots within the dialog box (not any of the buttons).')

with mouse.Listener(
        on_click=mouse_Location) as listener:
    listener.join()


click1pixel = pyscreeze.pixel(CLICK1[0], CLICK1[1])
click2pixel = pyscreeze.pixel(CLICK2[0], CLICK2[1])
click3pixel = pyscreeze.pixel(CLICK3[0], CLICK3[1])


print('Click on the okay button.')

with mouse.Listener(
        on_click=okay_Location) as listener:
    listener.join()


sleep(3)

print('Monitoring for dialog box. Please standby.')
print('Click Ctrl + C to shut down script manually.')

currentPixel1 = pyscreeze.pixelMatchesColor(CLICK1[0], CLICK1[1], click1pixel)
currentPixel2 = pyscreeze.pixelMatchesColor(CLICK2[0], CLICK2[1], click2pixel)
currentPixel3 = pyscreeze.pixelMatchesColor(CLICK3[0], CLICK3[1], click3pixel)

whileLoopCount = 0
imageCount = 1
while(imageCount < 1000):
    while(currentPixel1 == False and currentPixel2 == False and currentPixel3 == False):
        sleep(.25)
        currentPixel1 = pyscreeze.pixelMatchesColor(CLICK1[0], CLICK1[1], click1pixel)
        currentPixel2 = pyscreeze.pixelMatchesColor(CLICK2[0], CLICK2[1], click2pixel)
        currentPixel3 = pyscreeze.pixelMatchesColor(CLICK3[0], CLICK3[1], click3pixel)
        whileLoopCount += 1
        if whileLoopCount >= 240:
            print('One minute of no dialog box. Shutting down script automatically.')
            exit()
    else:
        imageCount += 1
        whileLoopCount = 0
        pyautogui.click(OKAY[0], OKAY[1])
        print('click ' + str(imageCount))
        #if imageCount == imageNumber:
        #    continue
        sleep(3)
        currentPixel1 = pyscreeze.pixelMatchesColor(CLICK1[0], CLICK1[1], click1pixel)
        currentPixel2 = pyscreeze.pixelMatchesColor(CLICK2[0], CLICK2[1], click2pixel)
        currentPixel3 = pyscreeze.pixelMatchesColor(CLICK3[0], CLICK3[1], click3pixel)


print('1000 images processed. Shutting down.')
