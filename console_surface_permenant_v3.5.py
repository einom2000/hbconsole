# check json twice to compare the failure
# use the list to locate in center
# ---------------above is v3.0 -------------------------------------------

# -----------------v3.5 version ------------------------------------------
# real_time checking online command
# /bin/command.json   not encrypted dictionary for command
# /bin/en.bin  encrypted dictionary with server public key, ready for sending
# /bin/keys_here.json keys of local private, server public, and local public, all non-encrypted
# /bin/server_ip.json store non-encrypted server address and port

# deleting all logging files which are 3 days ago
# to check size ration of the login window of btnet. Normal 4, other 5 tabs added, before key in.
# auto check midnight time to restart

# command 'pause' for quit and game and record the wins, and waiting for command'activated'
# command 'activated' resume the farming
# command 'cease' for stopping farming and wait for next day loop
# command 'quit' for quiting farming program.

# while start program, key in number required: 0 for all accounts, 23 for 2nd and 3rd account,
# 2 for 2nd account only, etc.

# --------------------------- v3.0 --------------------------------------
import os, win32api, random, json, keyboard, pickle
import win32gui, sys, winsound
import time
import pyautogui
import winshell, psutil, shutil
import cv2
from datetime import datetime
from datetime import timedelta
import logging
from win32api import GetKeyState
from win32con import VK_CAPITAL

# ----------------------communication related------------------------------
import rsa_encrypto
import communication
import client_sending


# farming_acc list from txt file, and save to pickle file
def generate_farming_list(account_txt, pickle_file):
    # change account_txt file to json
    with open(account_txt) as f:
        lines = f.readlines()
        total_account = int(lines[0][:-1])
        max_wins = [int(lines[1][:-1]), int(lines[5][:-1]), int(lines[9][:-1])]
        already_won = [0, 0, 0]
        account_id = (lines[2][:-1], lines[6][:-1], lines[10][:-1])
        account_psd = (lines[3][:-1], lines[7][:-1], lines[11][:-1])
        deck_list = (lines[4][:-1], lines[8][:-1], lines[12][:-1])

    farming_list = []
    for i in range(total_account):
        acc = {'acc': account_id[i],
               'psw': account_psd[i],
               'max': max_wins[i],
               'won': already_won[i],
               'dck': deck_list[0]}
        farming_list.append(acc)

    with open(pickle_file, 'wb') as f:
        pickle.dump(farming_list, f)

    return


# get farming list from the pickle file
def parse_farming_list_file(pickle_file):
    with open(pickle_file, 'rb') as f:
        lst = pickle.load(f)
    return lst


# deleting old log files
def clean_log_files():
    # clean all files 3 days ago
    valid_date = datetime.now() + timedelta(days=-3)
    for root, dirs, files in os.walk("C:\\Users\\Einom_Ng\\PycharmProjects\\hbconsole"):
        for file in files:
            if file.endswith(".log") and file.startswith("running_2"):
                log_date = datetime.strptime(file[-14: -4], "%Y-%m-%d")
                if log_date < valid_date:
                    filename = os.path.join(root, file)
                    os.remove(filename)
                    print('Deleting OLD LOG FILE: ', file=sys.stderr)
                    print(filename)


# get command for today's farming from a user
def get_and_parse_command(tf_list):
    # set all accounts won to max
    for role in tf_list:
        role['won'] = role['max']

    # asking for a command line
    print('There are %d account(s) in list, how do you want farm:' % len(sf_list), file=sys.stderr)
    time.sleep(0.5)
    i = 1
    for role in sf_list:
        print(i, end='   :')
        print(role['acc'])
        i += 1
    print('sample: 0 == farming all with default max win')
    print('        1 == farming 1st.acc with default max win')
    print('        2,3 == farming 2nd & 3rd with default max win')
    print('        1-20,3-10 == farming 1st.with 20wins, 3rd with 10wins')
    print('        0-20 == farming all with 20 wins')
    wrong_cmd = True
    # parse command, to win = max - won
    while wrong_cmd:
        commands = input('plsease give a command: ').split(',')
        if len(commands) == 1 and commands[0] == '0':
            for role in tf_list:
                role['won'] = 0
            wrong_cmd = False
        else:
            for cmd in commands:
                if cmd.replace(' ', '').isdigit() and int(cmd) <= len(tf_list):
                    tf_list[int(cmd) - 1]['won'] = 0
                    wrong_cmd = False
                elif cmd.count('-') == 1:
                    cmds = cmd.split('-')
                    if cmds[0].replace(' ', '').isdigit() and int(cmds[0]) <= len(tf_list) \
                                                          and cmds[1].replace(' ', '').isdigit() and int(cmds[1]) < 31:

                        tf_list[int(cmds[0]) - 1]['won'] = 31 - int(cmds[1])
                        wrong_cmd = False
                    else:
                        wrong_cmd = True
                        break
                else:
                    wrong_cmd = True
                    break
        if not wrong_cmd:
            return tf_list

        print('wrong command, try again', file=sys.stderr)
        time.sleep(0.3)


# click buddy's btn, a btn_name list with x, y should be given
def click_hb_btn(btn_name):
    time.sleep(0.3)
    pyautogui.moveTo(btn_name[0], btn_name[1], 0.5)
    time.sleep(0.2)
    pyautogui.click()


# kill certain process, process's name and window's name should be given
def kill_process(process_name, wd_name):
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == process_name:
            proc.kill()
            break
    while win32gui.FindWindow(None, wd_name):
        pass
    return


# login class
class LoginWindow:

    windowHwnd = 0

    def __init__(self, programdir, windowname, username, userpwd):
        self.programDir = programdir
        self.windowName = windowname
        self.userName = username
        self.userPwd = userpwd

    # load btnet
    def runbnet(self):
        exist = win32gui.FindWindow(None, self.windowName)
        if exist == 0:
            win32api.WinExec(self.programDir)
        return

    # looking for btnet window and return handle
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

    # login process
    def login(self):
        # to log in id
        # should check size ration of the login window of btnet. Normal 4, other 5  ********************
        tabs = 4
        # if the size ratio of the login window of btnet is in normal range?
        if False:
            tabs = 5
        for i in range(tabs):
            pyautogui.press('tab')
            time.sleep(random.uniform(3.0, 5.0) / 10)
        # clear box
        pyautogui.press('backspace')
        time.sleep(random.uniform(3.0, 5.0) / 10)
        # change to english
        pyautogui.press('shift')
        time.sleep(random.uniform(3.0, 5.0) / 10)
        win32api.LoadKeyboardLayout('00000409', 1)
        time.sleep(random.uniform(3.0, 5.0) / 10)
        # type in
        pyautogui.typewrite(self.userName, interval=(random.randint(15, 30) / 100))
        time.sleep((random.uniform(15.0, 30.0) / 100))
        pyautogui.press('tab')
        pyautogui.typewrite(self.userPwd, interval=(random.randint(15, 30) / 100))
        time.sleep(13)
        for i in range(3):
            pyautogui.press('tab')
            time.sleep(random.uniform(3.0, 5.0) / 10)
        # log in
        pyautogui.press('enter')
        return


# ------------------------- initialization -----------------------------------------------------------------------------
logging.basicConfig(filename='running_' + str(datetime.now().date()) + '.log', filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y--%H:%M:%S', level=logging.DEBUG)
logging.info('Program starts.')

# checking capslock is not activated.
while GetKeyState(VK_CAPITAL):
    pyautogui.press('capslock')
    logging.info('capslock released!')

# deleting old log files
clean_log_files()
logging.warning('OLD LOG FILES DELETED!')

# get standard farming list in to sf_list
generate_farming_list('account_per.txt', 'acc_farm_list.pcl')
sf_list = parse_farming_list_file('acc_farm_list.pcl')

# get today's farming order from a user
tf_list = get_and_parse_command(sf_list)
# so far we have tf_list to start farming and sf_list for the next day.
logging.info('standard_farming list and today_farming list all loaded!')


# --------------------------variables------------------------------------------------
bn_target = winshell.shortcut(os.path.join(winshell.desktop(), "暴雪战网.lnk")).path
hs_target = winshell.shortcut(os.path.join(winshell.desktop(), "炉石传说.lnk")).path

if os.path.basename(__file__) == 'console_surface_permenant_v3.5.py':
    logging.warning('script running on surface with an endless loop!')
    suffix = '_sur'
else:
    suffix = ''
    logging.warning('script running on other machine with an endless loop!')
logging.info('All variables were loaded.')

sys.exit()
# --------------------------main loop starts here-----------------------------------------------------------------------
while True:  # endless loop
    gold_miner_loop = True
    player_id = 0
    # in case break during one player's mining
    player_break = 0


    # wait for the midnight
    now = datetime.now()
    t = time.time()

    start_right_now = False
    # just for logging purpose:
    seconds_since_midnight = (datetime.now() - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    logging.info('shall wait for ' + str(int(86400 - seconds_since_midnight)) + ' seconds to start!')
    logging.info(str(total_account) + 'accounts to mine')

    # check hearthston folder   ------------ mono.dll and bnl_checkout_client.dll
    mono_path = os.path.split(hs_target)[0] + '\\Hearthstone_Data\\mono'
    target_mono_path = os.path.split(hs_target)[0] + '\\Hearthstone_Data\\mono\\etc'
    plugin_path = os.path.split(hs_target)[0] + '\\Hearthstone_Data\\plugins'
    # should be 2115520 not 2117056
    if os.path.isfile(os.path.join(mono_path, 'mono.dll')) and \
            os.path.getsize(os.path.join(mono_path, 'mono.dll')) != 2115520:
        shutil.move(os.path.join(mono_path, 'mono.dll'), os.path.join(target_mono_path, 'mono.dll'))
        print('move mono.dll to etc folder!')
    if os.path.isfile(os.path.join(mono_path, 'MonoPosixHelper.dll')):
        shutil.move(os.path.join(mono_path, 'MonoPosixHelper.dll'),
                    os.path.join(target_mono_path, 'MonoPosixHelper.dll'))
        print('move MonoPosixHelper.dll to etc folder!')
    if not os.path.isfile(os.path.join(mono_path, 'mono.dll')):
        shutil.copy(os.path.split(hs_target)[0] + '\\Hearthstone_Data\\mono.dll',
                    os.path.join(mono_path, 'mono.dll'))
        print('copy the 2066kb mono.dll to mono folder!')
    if os.path.isfile(os.path.join(plugin_path, 'bnl_checkout_client.dll')):
        shutil.move(os.path.join(plugin_path, 'bnl_checkout_client.dll'),
                    os.path.join(target_mono_path, 'bnl_checkout_client.dll'))
        print('move the bnl_checkout_client.dll to etc folder.')

    while not start_right_now:
        seconds_since_midnight = (datetime.now() - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        if seconds_since_midnight > 86400:
            break
        elif time.time() - t >= 10:
                print("There are still " + str(int(86400 - seconds_since_midnight)) + ' seconds to start!')
                print(str(total_account) + 'accounts to mine')
                print('Or you might press SPACE to skip!')
                t = time.time()
        elif keyboard.is_pressed('space'):
            winsound.Beep(500, 300)
            print('"space" was pressed, skip counting!')
            logging.info('"space" was pressed, skip counting!')
            time.sleep(3)
            start_right_now = True

    # main loop
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
            if time.time() - logging_time >= 6000:
                # after 10 minutes failure, terminate program
                logging.warning('logging keeps failing, terminated!')
                sys.exit()

        # logged in Battle net!!!
        # move bn window to 0,0
        win32gui.SetForegroundWindow(bt_window)
        bt_rec = win32gui.GetWindowRect(bt_window)
        if os.path.basename(__file__) == 'console_surface.py':
            win32gui.MoveWindow(bt_window, 0, 0, 1280, 820, 1)
            bt_rec = win32gui.GetWindowRect(bt_window)
        else:
            win32gui.MoveWindow(bt_window, 0, 0, bt_rec[2] - bt_rec[0], bt_rec[3] - bt_rec[1], 1)
        time.sleep(1)

        # looking for hs and click waiting for hs
        hs_png = 'hs' + suffix + '.png'
        while True:
            if os.path.basename(__file__) == 'console_surface.py':
                found = pyautogui.locateCenterOnScreen(hs_png, region=(10, 380, 300, 500),
                                                       grayscale=False, confidence=0.7)
            else:
                found = pyautogui.locateCenterOnScreen(hs_png, region=(0, 0, bt_rec[2], bt_rec[3]),
                                                       grayscale=False, confidence=0.7)
            if found is not None:
                x = found[0]
                y = found[1]
                break

        logging.info('hs logo found in (' + str(x) + ', ' + str(y) + ')!')
        pyautogui.moveTo(x, y, 1,  pyautogui.easeInQuad)
        pyautogui.click(x, y)
        time.sleep(1)
        login_png = 'login' + suffix + '.png'
        while True:
            if os.path.basename(__file__) == 'console_surface.py':
                found = pyautogui.locateCenterOnScreen(login_png, region=(450, 850, 880, 1000),
                                                       grayscale=False, confidence=0.7)
            else:
                found = pyautogui.locateCenterOnScreen(login_png, region=(0, 0, bt_rec[2], bt_rec[3]),
                                                       grayscale=False, confidence=0.7)
            if found is not None:
                x = found[0]
                y = found[1]
                logging.info('found the login button!')
                break
        pyautogui.moveTo(x, y, 1,  pyautogui.easeInQuad)
        pyautogui.click(x, y)
        logging.info('hs log in button was pressed!')

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
        win32gui.MoveWindow(hs_window, 620, 0, 800, 600, 1) # (90, 420)
        re_x = 90
        re_y = 420
        t = time.time()
        # (986, 355), (1055, 389)
        pyautogui.moveTo(739 + re_x, 116 + re_y, 1, pyautogui.easeInQuad)
        pyautogui.click()

        time.sleep(10)
        hs_rec = win32gui.GetWindowRect(hs_window)
        print(hs_rec)

        while time.time() - t <= 20:
            lost_confirm = pyautogui.locateCenterOnScreen('lost_confirmation_logo_new.png',
                                                          region=(950 + re_x, 300 + re_y, 400, 200),
                                                         grayscale=False, confidence=0.6)
            if lost_confirm is not None:
                pyautogui.moveTo(1000 + re_x, 375 + re_y, 1, pyautogui.easeInQuad)
                pyautogui.click()
                break

        # close bt window be set in comfigure of bn
        # kill_process('Battle.net.exe', '暴雪战网')
        time.sleep(15)
        logging.info('battlenet window was shut!')
        pyautogui.moveTo(850 + re_x, 200 + re_y, 1,  pyautogui.easeInQuad)
        pyautogui.click()
        # launching hb
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
        if suffix == "_sur":
            hs_wd_height = 790 + 400
        else:
            hs_wd_height = 790
        win32gui.MoveWindow(hb_window, 0, 0, 620, hs_wd_height, 1)
        hb_rec = win32gui.GetWindowRect(hb_window)

        # waiting and click start for buddy
        time.sleep(15)
        hb_png = 'hb_start' + suffix + '.png'
        while True:
            time.sleep(2)
            found_hb_start = pyautogui.locateCenterOnScreen(hb_png, region=(0, 0, hb_rec[2], hb_rec[3]),
                                                            grayscale=False, confidence=0.7)
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
        if suffix == "_sur":
            buddy_btn_dict = {'start_btn': (366, 180),
                              'setting_btn': (175, 236),
                              'default_bot_btn': (175, 279),
                              'mode_btn': (477, 608),
                              'rule_btn': (479, 653),
                              'deck_btn': (354, 697),
                              'stats_btn': (459, 278),
                              'stats_reset_btn': (83, 456),
                              'win_rec': [(84, 174), (116, 197)]}

        click_hb_btn(buddy_btn_dict['setting_btn'])
        click_hb_btn(buddy_btn_dict['default_bot_btn'])
        click_hb_btn(buddy_btn_dict['deck_btn'])
        # uncheck 2 boxes for cache
        pyautogui.moveTo(367, 445, 1, pyautogui.easeInQuad)
        pyautogui.click()
        time.sleep(2)
        pyautogui.moveTo(371, 488, 1, pyautogui.easeInQuad)
        pyautogui.click()
        time.sleep(2)
        # FOR UPDATE FROM APRIL 5TH MONO.DLL WAS RE-ALLOCATED
        HS_BATTLE_SELECTION_BTN = (1017 + re_x, 218 + re_y)
        HS_BATTLE_START_BTN = (1239 + re_x, 487 + re_y)
        HS_START_BTN_REGION = (1000 + re_x, 300 + re_y, 500, 500)
        SEARCHING_BOX = (900 + re_x, 100 + re_y, 400, 300)
        while True:
            time.sleep(random.randint(1000, 2000) / 1000)
            pyautogui.moveTo(HS_BATTLE_SELECTION_BTN[0], HS_BATTLE_SELECTION_BTN[1], 1, pyautogui.easeInQuad)
            time.sleep(random.randint(1000, 2000) / 1000)
            pyautogui.click()
            found_it = pyautogui.locateCenterOnScreen('START_NEW.png', region=HS_START_BTN_REGION,
                                                      grayscale=False, confidence=0.7)
            if found_it is not None:
                print(found_it)
                pyautogui.moveTo(HS_BATTLE_START_BTN[0], HS_BATTLE_START_BTN[1], 1, pyautogui.easeInQuad)
                pyautogui.click()
                time.sleep(random.randint(1000, 2000) / 1000)
                if pyautogui.locateCenterOnScreen('searching_new.png', region=SEARCHING_BOX,
                                                  grayscale=False, confidence=0.7) is not None:
                    break
        pyautogui.moveTo(850 + re_x, 200 + re_y, 1,  pyautogui.easeInQuad)
        pyautogui.click()
        click_hb_btn(buddy_btn_dict['start_btn'])
        logging.info('start the buddy.')
        time.sleep(1)
        click_hb_btn(buddy_btn_dict['stats_btn'])
        time.sleep(1)

        # if it is a new player start mining, reset counter
        click_hb_btn(buddy_btn_dict['stats_reset_btn'])
        logging.info('status info reset!')
        t = time.time()
        check_bug_start = True
        wild_logo_png = 'wild_logo' + suffix + '.png'
        wild_logo_rgn = (1231 + re_x, 33 + re_y, 1267, 69)
        if suffix == "_sur":
            wild_logo_rgn = (1220 + re_x, 45 + re_y, 1270, 90)
        t = time.time()
        checking_continue = True
        close_logo_png = 'close_logo' + suffix + '.png'
        close_logo_rgn = (900 + re_x, 100 + re_y, 1300, 500)
        break1_png = 'broke1' + suffix + '.png'
        break2_png = 'broke2' + suffix + '.png'
        break3_png = 'broke3' + suffix + '.png'
        break1_rgn = (750 + re_x, 260 + re_y, 840, 350)
        break2_rgn = (890 + re_x, 240 + re_y, 1160, 400)
        break3_rgn = (890 + re_x, 240 + re_y, 1160, 400)
        if suffix == '_sur':
            close_logo_rgn = (900 + re_x, 200 + re_y, 1300, 500)
        checking_period = 1000
        last_win = 0
        last_losses = 0
        last_concedes = 0
        general_failure = None
        while checking_continue:
            time.sleep(3)

            found_start = pyautogui.locateCenterOnScreen('START_NEW.png', region=HS_START_BTN_REGION,
                                                      grayscale=False, confidence=0.7)
            print(found_start)
            if found_start is not None:
                click_hb_btn(buddy_btn_dict['start_btn'])
                time.sleep(2)
                pyautogui.moveTo(HS_BATTLE_START_BTN[0], HS_BATTLE_START_BTN[1], 1, pyautogui.easeInQuad)
                pyautogui.click()
                time.sleep(random.randint(1000, 2000) / 1000)
                while True:
                    time.sleep(2)
                    if pyautogui.locateCenterOnScreen('searching_new.png', region=SEARCHING_BOX,
                                                  grayscale=False, confidence=0.7) is not None:
                        click_hb_btn(buddy_btn_dict['start_btn'])
                        break

            if time.time() - t >= checking_period - 10:
                logging.info('start to check the score...')
                # read score
                with open("Settings\Default\Stats.json") as json_file:
                    json_data = json.load(json_file)
                    logging.info('status shows: ' + str(json_data))
                    win_count = json_data['Wins']
                    lose_count = json_data['Losses']
                    concede_count = json_data['Concedes']
                    if int(win_count) >= (max_wins[player_id] - already_won):
                        logging.warning('player No.' + str(player_id) + ' got ' + str(win_count + already_won) + ' wins!')
                        logging.info('close hstone program.....')
                        kill_process('Hearthstone.exe', '炉石传说')
                        player_id += 1
                        already_won = 0
                        logging.info('shift to the next player...')
                        player_break = 0
                        checking_continue = False
                        if player_id >= total_account:
                            logging.warning('maxium players has been played....terminating...')
                            kill_process('Hearthstone.exe', '炉石传说')
                            gold_miner_loop = False
                            checking_continue = False
                            check_bug_start = False
                        # time.sleep(30)
                        break
                    if int(win_count) == last_win and int(lose_count) == last_losses and \
                            int(concede_count) == last_concedes:
                        general_failure = 'Not None"'
                    else:
                        last_win = int(win_count)
                        last_losses = int(lose_count)
                        last_concedes = int(concede_count)

                # (1231, 33)(1267, 69) check failure

                failure_found_1 = pyautogui.locateCenterOnScreen(close_logo_png, region=close_logo_rgn,
                                                                 grayscale=False, confidence=0.7)
                failure_found_2 = None  # disable break1 png
                failure_found_3 = pyautogui.locateCenterOnScreen(break2_png, region=break2_rgn,
                                                                 grayscale=False, confidence=0.7)
                failure_found_4 = pyautogui.locateCenterOnScreen(break3_png, region=break3_rgn,
                                                                 grayscale=False, confidence=0.7)
                if failure_found_1 is not None or general_failure is not None\
                        or failure_found_3 is not None or failure_found_4 is not None:
                    print(failure_found_1, failure_found_2, failure_found_3, failure_found_4, general_failure)
                    logging.warning('game disconnected.....')
                    with open("Settings\Default\Stats.json") as json_file:
                        json_data = json.load(json_file)
                        logging.info('status shows: ' + str(json_data))
                        win_count = json_data['Wins']
                        already_won += int(win_count)
                    logging.info(str((account_id[player_id]) + ' fails ' + str(player_break) + ' times!'))
                    logging.info('Player won ' + str(already_won) + ' games before broken')
                    time.sleep(60)
                    logging.info('close hstone program.....')
                    kill_process('Hearthstone.exe', '炉石传说')
                    player_break += 1
                    logging.info('adding one more failure...')
                    checking_continue = False
                    break
                t = time.time()
