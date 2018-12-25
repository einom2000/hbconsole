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


import os, win32api,random
import win32gui,sys
import time
import pyautogui
import win32com.client
import win32process as process
import winshell, psutil


def kill_process(process_name, wd_name):
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == process_name:
            proc.kill()
    while win32gui.FindWindow(None, wd_name):
         pass
    return

class LoginWindow:

    windowHwnd = 0

    def __init__(self, programdir, windowname, username, userpwd):
        self.programDir = programdir
        self.windowName = windowname
        self.userName = username
        self.userPwd = userpwd

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
            break
        win32gui.SetForegroundWindow(hwndbnt)
        time.sleep(0.5)
        return hwndbnt

    def login(self):
        # to log in id
        for i in range(4):
            pyautogui.press('tab')
            time.sleep(random.randint(3, 5) / 10)
        # clear box
        pyautogui.press('backspace')
        time.sleep(random.randint(3, 5) / 10)
        # change to english
        pyautogui.press('shift')
        time.sleep(random.randint(3, 5) / 10)
        win32api.LoadKeyboardLayout('00000409', 1)
        time.sleep(random.randint(3, 5) / 10)
        # typein
        pyautogui.typewrite(self.userName, interval=(random.randint(15, 30) / 100))
        time.sleep((random.randint(15, 30) / 100))
        pyautogui.press('tab')
        pyautogui.typewrite(self.userPwd, interval=(random.randint(15, 30) / 100))
        for i in range(3):
            pyautogui.press('tab')
            time.sleep(random.randint(3, 5) / 10)
        # log in
        pyautogui.press('enter')
        return


hb_dir = 'D:\hb\\'
bn_target = winshell.shortcut(os.path.join(winshell.desktop(), "暴雪战网.lnk")).path
hs_target = winshell.shortcut(os.path.join(winshell.desktop(), "Hearthstone.exe - 快捷方式.lnk")).path
hb_target = hb_dir + os.readlink(os.path.join(hb_dir, "Hearthbuddy.exe"))
hearthstone = 'D:\Program Files (x86)\Hearthstone\Hearthstone_Data'
loginbt = LoginWindow(bn_target, '暴雪战网登录', 'einom2000@163.com', '123NUNUchipi')

logged_in = False
logging_time = time.time()
while not logged_in:
    loginbt.runbnet()
    bn_hwnd = loginbt.findWindow()
    loginbt.login()
    # wait for the battle net window shows up
    time_login = time.time()
    while time.time() - time_login <= 30:
        bt_window = win32gui.FindWindow(None, '暴雪战网')
        if bt_window > 0:
            logged_in = True
            break
    if not logged_in:
        kill_process('Battle.net.exe', '暴雪战网登录')
    if time.time() - logging_time >= 600:
        # after 10 minutes failure, terminate program
        sys.exit()

# logged in Battle net!!!













