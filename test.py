import pyautogui
import time
import keyboard

while True:
    if keyboard.is_pressed('space'):
        print(pyautogui.position())
    time.sleep(.5)
