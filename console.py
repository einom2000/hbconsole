# open bt shortcut on desktop
# log in bt
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
import win32process as process



class LoginWindow:
    windowUpLeftX = 0
    windowUpLeftY = 0
    windowHwnd = 0

    def __init__(self, programdir, windowname, username, userpwd):
        self.programDir = programdir
        self.windowName = windowname
        self.userName = username
        self.userPwd = userpwd

    def runbnet(self):
        win32api.WinExec(self.programDir)
        return

    def findWindow(self):
        while True:
            hwndbnt = win32gui.FindWindow(None, self.windowName)
            if hwndbnt == 0:
                continue
            else:
                rect = win32gui.GetWindowRect(hwndbnt)
            break
        win32gui.SetForegroundWindow(hwndbnt)
        time.sleep(0.5)
        return hwndbnt, rect[0], rect[1]

    def login(self):
        battlenetAccoutWindowX = self.windowUpLeftX + 400
        battlenetAccoutWindowY = self.windowUpLeftY + 250
        pyautogui.moveTo(battlenetAccoutWindowX, battlenetAccoutWindowY, 2, pyautogui.easeInOutQuad)
        pyautogui.click()
        t = time.time()
        while time.time() - t <= 5:
            pyautogui.press('backspace')
        if win32api.GetKeyboardLayout() == 134481924:
            pyautogui.press('shift')
            print(win32api.GetKeyboardLayout())
            time.sleep(0.25)
        pyautogui.typewrite(self.userName, interval=0.25)
        time.sleep(0.25)
        pyautogui.press('tab')
        pyautogui.typewrite(self.userPwd, interval=0.25)


bt_shortcut = desktop = os.path.expanduser("~/Desktop/")'D:\Program Files (x86)\Battle.net\Battle.net Launcher.exe'
hearthstone = 'D:\Program Files (x86)\Hearthstone\Hearthstone_Data'
loginbt = LoginWindow(battlenet, '暴雪战网登录', 'einom2000@163.com', '123NUNUchipi')

loginbt.runbnet()
btwindowInfo = loginbt.findWindow()

loginbt.windowHwnd = btwindowInfo[0]
loginbt.windowUpLeftX = btwindowInfo[1]
loginbt.windowUpLeftY = btwindowInfo[2]
print(loginbt.windowHwnd, loginbt.windowUpLeftX, loginbt.windowUpLeftY)

loginbt.login()










