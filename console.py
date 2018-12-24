# open bn shortcut on desktop
# log in bn
# switch to hs
# check files and
# remove file:
# run
# wait and enter the deck
# run hb D:\hb\ symlink
# wait and click start
# monitor the hb start button and the win times
# monitor the hs window status


import os, win32api
import win32gui,sys
import time
import pyautogui
import win32com.client
import win32process as process
import winshell
# from win32api import GetSystemMetrics
#
# SYS_WIDTH = GetSystemMetrics(0)
# SYS_HEIGHT = GetSystemMetrics(1)

def kill_process(process_name):
    pass

class LoginWindow:
    windowUpLeftX = 0
    windowUpLeftY = 0
    windowHwnd = 0

    def __init__(self, programdir, windowname, username, userpwd):
        self.programDir = programdir
        self.windowName = windowname
        self.userName = username
        self.userPwd = userpwd
        self.rect = ()

    def runbnet(self):
        exist = win32gui.FindWindow(None, self.windowName)
        if exist == 0:
            win32api.WinExec(self.programDir)
        return

    def findWindow(self):
        while True:
            hwndbnt = win32gui.FindWindow(None, self.windowName)
            if hwndbnt == 0:
                continue
            else:
                win32gui.MoveWindow(hwndbnt, 100, 100, 365, 541, True)
                self.rect = win32gui.GetWindowRect(hwndbnt)
                print(self.rect)
            break
        win32gui.SetForegroundWindow(hwndbnt)
        time.sleep(0.5)
        return hwndbnt, self.rect[0], self.rect[1]

    def login(self):
        battlenetAccoutWindowX = self.windowUpLeftX + int(200 / 365 * self.rect[2])
        battlenetAccoutWindowY = self.windowUpLeftY + int(230 / 541 * self.rect[3])
        pyautogui.moveTo(battlenetAccoutWindowX, battlenetAccoutWindowY, 0.8, pyautogui.easeInOutQuad)
        print(pyautogui.position())
        pyautogui.click()
        t = time.time()
        while time.time() - t <= 5:
            pyautogui.press('backspace')
        win32api.LoadKeyboardLayout('00000409', 1)
        time.sleep(0.5)
        # if win32api.GetKeyboardLayout() == 134481924:
        #     pyautogui.press('shift')
        #     # print(win32api.GetKeyboardLayout())
        #     time.sleep(0.25)
        pyautogui.typewrite(self.userName, interval=0.25)
        time.sleep(0.25)
        pyautogui.press('tab')
        pyautogui.typewrite(self.userPwd, interval=0.25)
        btnhdl = win32gui.FindWindowEx(self.windowHwnd, 0, "Button", "登录")
        return btnhdl


hb_dir = 'D:\hb\\'
bn_target = winshell.shortcut(os.path.join(winshell.desktop(), "暴雪战网.lnk")).path
# hs_target = winshell.shortcut(os.path.join(winshell.desktop(), "Hearthstone.exe - 快捷方式.lnk")).path
# hb_target = hb_dir + os.readlink(os.path.join(hb_dir, "Hearthbuddy.exe"))

# hearthstone = 'D:\Program Files (x86)\Hearthstone\Hearthstone_Data'
loginbt = LoginWindow(bn_target, '暴雪战网登录', 'einom2000@163.com', '123NUNUchipi')

loginbt.runbnet()
btwindowInfo = loginbt.findWindow()
loginbt.windowHwnd = btwindowInfo[0]
loginbt.windowUpLeftX = btwindowInfo[1]
loginbt.windowUpLeftY = btwindowInfo[2]
print(loginbt.windowHwnd, loginbt.windowUpLeftX, loginbt.windowUpLeftY)

print(loginbt.login())











