import win32gui
import win32process
import re
import keyboard
import pyautogui
import time
import os
import glob


def enumHandler(hwnd, lParam):
    global ranger_txt, ranger_hwnd
    keywords = ['ycharm', '炉石', '暴雪', '设置', 'Program',
                'Microsoft', 'MainWindow','Chrome']
    if win32gui.IsWindowVisible(hwnd):
        wintitle = win32gui.GetWindowText(hwnd)
        if len(wintitle) <= 0 or any(key in wintitle for key in keywords):
            pass
        elif re.match("^[a-z0-9+]*$", wintitle):
            print(win32gui.GetWindowText(hwnd), end=' ----->  ')
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            print(r'pid = %s' % str(found_pid))
            print(r'hwnd= %s' % str(hwnd))
            ranger_txt = wintitle
            ranger_hwnd = hwnd


ranger_txt = ''
ranger_hwnd = 0
win32gui.EnumWindows(enumHandler, None)
if ranger_txt is not '':
    print(r'here is the window title %s!' % ranger_txt)
    print(r'here is the handler of that window %d !' % ranger_hwnd)
    width = win32gui.GetWindowRect(ranger_hwnd)[2]
    win32gui.MoveWindow(ranger_hwnd, 0, 0, width, 700, True)
    win32gui.SetForegroundWindow(ranger_hwnd)


ranger_start_button = (368, 267)


pyautogui.moveTo(ranger_start_button[0], ranger_start_button[1])


newest = max(glob.iglob('c:\\HearthRanger\\HearthRanger\\task_log\\*.log'), key=os.path.getctime)

print(newest)

for line in reversed(open(newest).readlines()):
    print(line.rstrip())