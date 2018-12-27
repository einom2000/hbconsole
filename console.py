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


import os, win32api,random,json, keyboard
import win32gui,sys
import time
import pyautogui
import win32com.client
import win32process as process
import winshell, psutil
import cv2
from datetime import datetime

import logging
logging.basicConfig(filename='running.log', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('Program starts.')


def click_hb_btn(btn_name):
    time.sleep(0.3)
    pyautogui.moveTo(btn_name[0], btn_name[1], 0.5)
    time.sleep(0.2)
    pyautogui.click()

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


f = open("account.txt", "r")
lines = f.readlines()
account_id = (lines[0][:-1], lines[3][:-1], lines[6][:-1])
account_psd = (lines[1][:-1], lines[4][:-1], lines[7][:-1])
deck_list = (lines[2][:-1], lines[5][:-1], lines[8][:-1])
f.close()
bn_target = winshell.shortcut(os.path.join(winshell.desktop(), "暴雪战网.lnk")).path
hs_target = winshell.shortcut(os.path.join(winshell.desktop(), "Hearthstone.exe - 快捷方式.lnk")).path


gold_miner_loop = True
player_id = 0
# in case break during one player's mining
player_break = 0

logging.info('All variables were loaded.')

#wait for the midnight
from datetime import datetime
now = datetime.now()
t = time.time()

start_right_now = False
# just for logging purpose:
seconds_since_midnight = (datetime.now() - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
logging.info('shall wait for ' + str(int(86400 - seconds_since_midnight)) + ' seconds to start!')

while not start_right_now:
    seconds_since_midnight = (datetime.now() - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    if seconds_since_midnight > 86400:
        break
    elif time.time() - t >= 10:
            print("There are still " + str(int(86400 - seconds_since_midnight)) + ' seconds to start!')
            print('Or you might press SPACE to skip!')
            t = time.time()
    elif keyboard.is_pressed('space'):
        print('"space" was pressed, skip counting!')
        logging.info('"space" was pressed, skip counting!')
        start_right_now = True

#main loop
while gold_miner_loop:
    logging.info('miner No.' + str(player_id) + ' player starts.')

    # open in battle net login window
    loginbt = LoginWindow(bn_target, '暴雪战网登录', account_id[player_id], account_psd[player_id])
    logged_in = False
    logging_time = time.time()
    bt_window = 0
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
                logging.info('logging No.' + str(player_id) + ' player succeeded!')
                break
        if not logged_in:
            kill_process('Battle.net.exe', '暴雪战网登录')
            logging.warning('log No.' + str(player_id) + ' player failed!')
        if time.time() - logging_time >= 600:
            # after 10 minutes failure, terminate program
            logging.warning('logging keeps failing, terminated!')
            sys.exit()

    # logged in Battle net!!!
    # move bn window to 0,0
    win32gui.SetForegroundWindow(bt_window)
    bt_rec = win32gui.GetWindowRect(bt_window)
    win32gui.MoveWindow(bt_window, 0, 0, bt_rec[2] - bt_rec[0], bt_rec[3] - bt_rec[1], 1)
    time.sleep(1)

    # looking for hs and click waiting for hs
    while True:
        found = pyautogui.locateCenterOnScreen('hs.png', region=(0, 0, bt_rec[2], bt_rec[3]),
                                               grayscale=False, confidence=0.9)
        if found is not None:
            x = found[0]
            y = found[1]
            break

    logging.info('hs logo found in (' + str(x) + ', ' + str(y) + ')!')
    pyautogui.moveTo(x, y, 1,  pyautogui.easeInQuad)
    pyautogui.click(x, y)
    time.sleep(1)
    x, y = pyautogui.locateCenterOnScreen('login.png', region=(0, 0, bt_rec[2], bt_rec[3]),
                                          grayscale=False, confidence=0.9)
    pyautogui.moveTo(x, y, 1,  pyautogui.easeInQuad)
    pyautogui.click(x, y)

    # waiting for hs running
    hs_is_running = False
    hs_window = 0
    logging.info('waiting for hstone loaded...')
    while not hs_is_running:
        hs_window = win32gui.FindWindow(None,'炉石传说')
        if hs_window > 0:
            hs_is_running = True
    logging.info('hstone loaded successfully!')
    time.sleep(3)
    win32gui.SetForegroundWindow(hs_window)
    hs_rec = win32gui.GetWindowRect(hs_window)
    win32gui.MoveWindow(hs_window, 620, 0, 800, 600, 1)

    # close bt window
    kill_process('Battle.net.exe', '暴雪战网')
    logging.info('battlenet window was shut!')

    #lauching hb
    logging.info('start to load buddy...')
    win32api.WinExec('Hearthbuddy.exe')
    while True:
        config_window = win32gui.FindWindow(None, 'Configuration Window')
        if config_window > 0:
            win32gui.SetForegroundWindow(config_window)
            logging.info('buddy configure shown up!')
            time.sleep(2)
            pyautogui.press('enter')
            time.sleep(1)
            break

    # wait for buddy's main window
    hb_is_running = False
    hb_window = 0
    while not hb_is_running:
        hb_window = win32gui.FindWindow(None, 'Hearthbuddy[0.3.1446.417] 学习交流,免费使用,严禁贩卖!')
        if hb_window > 0:
            hb_is_running = True
            logging.info('buddy main window shown up!')
    time.sleep(2)
    hb_rec = win32gui.GetWindowRect(hb_window)
    win32gui.MoveWindow(hb_window, 0, 0, 620, 790, 1)

    #waiting and click start for hbuddy
    time.sleep(5)
    while True:
        found_hb_start = pyautogui.locateCenterOnScreen('hb_start.png', region=(0, 0, hb_rec[2], hb_rec[3]),
                                                        grayscale=False, confidence=0.8)
        if found_hb_start:
            logging.info('buddy start button found, buddy ready!')
            break
    # start to set monitor

    buddy_btn_dict = {'start_btn': found_hb_start,
                      'setting_btn': (99, 137),
                      'default_bot_btn': (99, 160),
                      'mode_btn': (269, 344),
                      'rule_btn': (270, 374),
                      'deck_btn': (201, 400),
                      'stats_btn': (267, 159),
                      'stats_reset_btn': (49, 260),
                      'win_rec': [(84, 174), (116, 197)]}

    click_hb_btn(buddy_btn_dict['setting_btn'])
    click_hb_btn(buddy_btn_dict['default_bot_btn'])
    click_hb_btn(buddy_btn_dict['deck_btn'])
    logging.info('trying to type in the right deck\'s name...')

    for i in range(20):
        pyautogui.press('backspace')
        pyautogui.press('delete')
        time.sleep(0.1)
    pyautogui.press('shift')
    pyautogui.typewrite(deck_list[player_id], interval=(random.randint(15, 30) / 100))
    time.sleep(2)
    click_hb_btn(buddy_btn_dict['start_btn'])
    logging.info('start the buddy.')
    time.sleep(1)
    click_hb_btn(buddy_btn_dict['stats_btn'])
    time.sleep(1)

    #if it is a new player start mining, reset counter
    if player_break == 0:
        click_hb_btn(buddy_btn_dict['stats_reset_btn'])
        logging.info('status info reset!')
    t = time.time()
    check_bug_start = True
    while check_bug_start:
        check_bug = pyautogui.locateCenterOnScreen('wild_logo.png', region=(1231, 33, 1267, 69),
                                                   grayscale=False, confidence=0.8)
        if check_bug is not None:
            logging.warning('buddy deck bugs found!')
            # click stop
            time.sleep(0.5)
            click_hb_btn(buddy_btn_dict['start_btn'])
            logging.info('stop the buddy.')
            time.sleep(3)
            time.sleep(0.5)
            click_hb_btn(buddy_btn_dict['default_bot_btn'])
            time.sleep(3)
            click_hb_btn(buddy_btn_dict['rule_btn'])
            logging.info('change the rules...')
            time.sleep(0.5)
            # if the first time bug
            if player_break == 0 or player_break % 2 == 0:
                pyautogui.press('up')
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(2)
                player_break += 1
                click_hb_btn(buddy_btn_dict['start_btn'])
                logging.info('buddy restarted..')
                time.sleep(2)
                click_hb_btn(buddy_btn_dict['stats_btn'])
            elif player_break % 2 == 1:
                pyautogui.press('down')
                time.sleep(0.5)
                pyautogui.press('down')
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(2)
                player_break += 1
                click_hb_btn(buddy_btn_dict['start_btn'])
                logging.info('buddy restarted..')
                # double check the start button?
                # while True:
                #     time.sleep(5)
                #     chck = pyautogui.locateCenterOnScreen('hb_start.png', region=(0, 0, hb_rec[2], hb_rec[3]),
                #                                           grayscale=False, confidence=0.8)
                #     if chck is None:
                #         break
                #     click_hb_btn(buddy_btn_dict['start_btn'])
                time.sleep(2)
                click_hb_btn(buddy_btn_dict['stats_btn'])
            t = time.time()
        if time.time() - t >= 300:
            check_bug_start = False
            logging.info('buddy running so fine!')
    #loop to check score and dead every 10 minuites
    t = time.time()
    checking_continue = True
    # win_count = 0
    # last_json_data = ''
    while checking_continue:
        if time.time() - t >= 600:
            logging.info('start to check the score...')
            # read score
            with open("Settings\Default\Stats.json") as json_file:
                json_data = json.load(json_file)
                logging.info('status shows: ' + str(json_data))
                win_count = json_data['Wins']
                if int(win_count) >= 32:
                    logging.warning('player No.' + str(player_id) + ' got ' + str(win_count) + ' wins!')
                    logging.info('close hstone program.....')
                    kill_process('Hearthstone.exe', '炉石传说')
                    player_id += 1
                    logging.info('shift to the next player...')
                    player_break = 0
                    checking_continue = False
                    if player_id >= 3:
                        logging.warning('maxium players has been played....terminating...')
                        sys.exit()
                    break
            # (1231, 33)(1267, 69) check failure
            failure_found = pyautogui.locateCenterOnScreen('close_logo.png', region=(1200, 25, 1300, 80),
                                                           grayscale=False, confidence= 0.8)
            if failure_found is not None:
                logging.warning('game disconnected.....')
                logging.info(str((account_id[player_id]) + ' fails ' + str(player_break) + ' times!'))
                logging.info('close hstone program.....')
                kill_process('Hearthstone.exe', '炉石传说')
                player_break += 1
                logging.info('adding one more failure...')
                checking_continue = False
                break
            t = time.time()
















