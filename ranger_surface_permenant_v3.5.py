# -- 32 wins switcher for ranger
# other set is for ranger

# --------------------------- v3.0 --------------------------------------
import os, win32api, random, json, keyboard, pickle, random
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
import re, glob


# ----------------------communication related------------------------------
import rsa_encrypto
import communication
import client_sending

import win32process



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
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".log") and file.startswith("ranger_running_2"):
                log_date = datetime.strptime(file[-14: -4], "%Y-%m-%d")
                if log_date < valid_date:
                    filename = os.path.join(root, file)
                    os.remove(filename)
                    print('Deleting OLD LOG FILE: ', file=sys.stderr)
                    print(filename)


# get command for today's farming from a user
def get_and_parse_command():
    global sf_list
    while True:
        # set all accounts won to max
        tf_list = []
        for role in sf_list:
            new_role = role.copy()
            tf_list.append(new_role)

        for role in tf_list:
            role['won'] = role['max']
        tmp_list = []
        flag = 0  # 0 for temp command # 1 for change configure permanently
        permanent_changes = []
        # asking for a command line
        print('MAKE SURE YOU START RANGER FIRST!!!', file=sys.stdout)
        time.sleep(0.6)
        print('There are %d account(s) in list, how do you want farm:' % len(sf_list), file=sys.stderr)
        time.sleep(0.5)

        i = 1
        for role in tf_list:
            print(i, end='   :')
            print(role['acc'])
            i += 1
        print('sample: 0 == farming all with default max win')
        print('        1 == farming 1st.acc with default max win')
        print('        3,2 == farming 3rd & 2nd with default max win in the temp order')
        print('        3-10, 1-20 == farming 3rd with 10wins, 1st.with 20wins in the temp order')
        print('        B,C,A,20 == CHANGE CONFIG PERMANENTLY IN THAT ORDER 2,3,1 WITH MAX 20 WINS')
        print('        If you are using ranger the wins counts are set by ranger\'s default!!!')

        wrong_cmd = True
        # parse command, to win = max - won
        while wrong_cmd:
            commands = input('please give a command: ').split(',')
            if len(commands) == 1 and commands[0] == '0':
                for role in tf_list:
                    role['won'] = 0
                return tf_list
            else:
                for cmd in commands:
                    cmd = cmd.replace(' ', '')
                    if cmd.isdigit() and int(cmd) <= len(tf_list) and not flag:
                        tf_list[int(cmd) - 1]['won'] = 0
                        tmp_list.append(tf_list[int(cmd) - 1].copy())
                        wrong_cmd = False
                    elif cmd.count('-') == 1 and not flag:
                        cmds = cmd.split('-')
                        if cmds[0].isdigit() and int(cmds[0]) <= len(tf_list) \
                                and cmds[1].isdigit() and int(cmds[1]) < 31:
                            tf_list[int(cmds[0]) - 1]['won'] = 32 - int(cmds[1])
                            dic = tf_list[int(cmds[0]) - 1].copy()
                            tmp_list.append(dic)
                            wrong_cmd = False
                        else:
                            wrong_cmd = True
                            break
                    elif cmd.isalpha() and len(cmd) == 1 and ord(cmd.upper()) - ord('A') <= len(tf_list) - 1 \
                            and flag != 1:
                        flag = 2
                        permanent_changes.append(ord(cmd.upper()) - ord('A'))
                    elif flag == 2 and cmd.isdigit() and 0 <= int(cmd) <= 35 and \
                            len(permanent_changes) <= len(tf_list):
                        permanent_changes.append(int(cmd))
                        wrong_cmd = False
                        flag = 1
                    else:
                        wrong_cmd = True
                        break
            if not wrong_cmd and flag == 0:
                if tmp_list is not None:
                    tf_list = tmp_list
                return tf_list
            elif not wrong_cmd and flag == 1:
                break
            else:
                flag = 0
                tmp_list = []
                permanent_changes = []
                print('wrong command, try again', file=sys.stderr)
                time.sleep(0.3)

        print('the order you changed is as following %s' % str(permanent_changes[:-1]), file=sys.stderr)
        print('the max wins are to be set to %s' % str(permanent_changes[-1]), file=sys.stderr)
        print('the configuration file will be changed permanently!', file=sys.stderr)
        time.sleep(0.5)
        k = input('please type \'Yes\' to confirm!')
        if k.upper() == 'Y' or k.upper() == 'YES':
            tmp_list = []
            for i in permanent_changes[:-1]:
                tmp_list.append(str(permanent_changes[-1]))
                tmp_list.append(tf_list[i]['acc'])
                tmp_list.append(tf_list[i]['psw'])
                tmp_list.append(tf_list[i]['dck'])

            d = [str(len(tf_list)) + '\n', ]
            for i in tmp_list:
                d.append(i + '\n')
            d.append(' \n')
            d.append(' \n')
            d.append('----generated by program with user order on ' + str(datetime.now()))

            with open('account_per.txt', 'w') as f:
                f.writelines(d)

            print('**************************************************', file=sys.stderr)
            print('configure file revised! please give an order again', file=sys.stderr)
            print('**************************************************', file=sys.stderr)
            time.sleep(0.3)
            generate_farming_list('account_per.txt', 'acc_farm_list.pcl')
            sf_list = parse_farming_list_file('acc_farm_list.pcl')
        else:
            pass


# click buddy's btn, a btn_name list with x, y should be given
def click_hb_btn(btn_name):
    move_and_click((btn_name[0], btn_name[1]))


# kill certain process, process's name and window's name should be given
def kill_process(process_name, wd_name):
    while win32gui.FindWindow(None, wd_name):
        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == process_name:
                proc.kill()
                break


def is_not_midnight():
    now = datetime.now()
    seconds_since_midnight = (
            datetime.now() - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    if seconds_since_midnight > 86380 or seconds_since_midnight < 20:
        return False
    else:
        return seconds_since_midnight


# wait for midnight
def wait_for_midnight():
    t = time.time()
    logging.info('start to wait for the midnight or for the user to start to command.')
    while True:
        seconds_since_midnight = is_not_midnight()
        if not seconds_since_midnight:
            time.sleep(20)
            return True
        elif time.time() - t >= 10:
            print("There are still " + str(int(86400 - seconds_since_midnight)) + ' seconds to start!')
            print(str(len(sf_list)) + ' accounts to farm.', file=sys.stderr)
            print('Or you might press SPACE to skip!', file=sys.stderr)
            t = time.time()
        elif keyboard.is_pressed('space'):
            winsound.Beep(500, 300)
            print('"space" was pressed, skip waiting for midnight!')
            logging.info('"space" was pressed, skip waiting for midnight, direct to user command input.')
            time.sleep(3)
            return False


# log in to bnet and check for size of the correct size of bnet window
def log_in_hs(acc):
    logging.info('miner No.' + str(player_id) + ' player starts.')
    # open in battle net login window
    loginbt = LoginWindow(bn_target, '暴雪战网登录', acc['acc'], acc['psw'])
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
        if time.time() - logging_time >= 1200:
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
    hs_png = 'hs_sur.png'
    while True:
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
    login_png = 'login_sur.png'
    while True:
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
        hs_window = win32gui.FindWindow(None, '炉石传说')
        if hs_window > 0:
            hs_is_running = True
    logging.info('hstone loaded successfully!')
    return hs_window


# enumlater for locate random name of the ranger window
def enumHandler1(hwnd, lParam):
    global ranger_txt, ranger_hwnd
    keywords = ['ycharm', '炉石', '暴雪', '设置', 'Program',
                'Microsoft', 'MainWindow', 'Chrome']
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

# adjust the hs window and click away the lost_game confirmation button
# ***** select deck and style and mounting in future
def initialize_hs_window(hs_window):
    win32gui.SetForegroundWindow(hs_window)
    time.sleep(10)
    hs_rec = win32gui.GetWindowRect(hs_window)
    print('found hs_window at %s!' % str(hs_rec), sys.stderr)


# load ranger...(ranger alway runs and click stay on top button off
def load_and_initiate_ranger():
    # looking for  ranger
    global ranger_txt, ranger_hwnd
    logging.info('start to look for ranger windows...')
    win32gui.EnumWindows(enumHandler1, None)
    if ranger_txt is not '':
        print(r'here is the window title %s!' % ranger_txt)
        print(r'here is the handler of that window %d !' % ranger_hwnd)
        width = win32gui.GetWindowRect(ranger_hwnd)[2]
        win32gui.MoveWindow(ranger_hwnd, 0, 0, width, 700, True)
        win32gui.SetForegroundWindow(ranger_hwnd)

    pyautogui.moveTo(ranger_btn_dict['start_btn'][0], ranger_btn_dict['start_btn'][1],  1,  pyautogui.easeInQuad)
    logging.info('ranger start button found, ranger is ready!')


# start a new buddy round
def start_ranger():
    # make sure the buddy_status is correct
    click_hb_btn(ranger_btn_dict['start_btn'])
    time.sleep(3)


# reset ranger win counter
def reset_status():
    time.sleep(2)
    click_hb_btn(ranger_btn_dict['config_btn'])
    time.sleep(5)
    click_hb_btn(ranger_btn_dict['auto_stop_sheet'])
    time.sleep(2)
    click_hb_btn(ranger_btn_dict['reset_win_counter_btn'])
    time.sleep(2)
    click_hb_btn(ranger_btn_dict['save_config_btn'])
    logging.info('ranger win counter reseted!')


# ============= find the last normal exit ================= 'Bot stopped'==========
# as well as find the last abnormal stop
def check_bot_stopped(file, default_start_time, last_check_time):
    format = '%H:%M:%S'
    newest_stop_log = max(glob.iglob(file), key=os.path.getctime)   #'c:\\HearthRanger\\task_log\\test\\*.log'

    last_normal_stop = ''
    previous_line = ''
    last_abnormal_stop = ''
    last_pause = ''

    for line in reversed(open(newest_stop_log, encoding='utf-8').readlines()):
        if line.lower().find('bot pause') >= 0 and last_pause == '':
            last_pause = line.strip()[0:8]
        elif line.find('Bot stopped.') >= 0:
            previous_line = 'Bot stopped.'
        elif previous_line == 'Bot stopped.' and \
                line.find('Game client closed by CloseGameAfterAutoStopped settings.') >= 0 and \
                last_normal_stop == '':
                    last_normal_stop = line.strip()[0:8]
                    if last_abnormal_stop != '':
                        break
        elif previous_line == 'Bot stopped.' and \
                line.find('Game client closed by CloseGameAfterAutoStopped settings.') < 0  and \
                last_abnormal_stop == '':
                    last_abnormal_stop = line.strip()[0:8]
                    if last_normal_stop != '':
                        break
        else:
            previous_line = ''

    if last_normal_stop != '':
        last_normal_stop_time = datetime.combine(datetime.now().date(),
                                                 datetime.strptime(last_normal_stop, format).time())
        print('Game client closed by CloseGameAfterAutoStopped settings.:', end=" ")
        print(last_normal_stop_time)
    else:
        last_normal_stop_time = default_start_time
    if last_abnormal_stop != '':
        last_abnormal_stop_time = datetime.combine(datetime.now().date(),
                                                   datetime.strptime(last_abnormal_stop, format).time())
        print('Game client last abnormal stoped at :', end='')
        print(last_abnormal_stop_time)
    else:
        last_abnormal_stop_time = default_start_time
    if last_pause != '':
        last_pause_time = datetime.combine(datetime.now().date(),
                                           datetime.strptime(last_pause, format).time())

        print('Game last pause at: ', end='')
        print(last_pause_time)
    else:
        last_pause_time = default_start_time

    # return checking result
    if last_normal_stop_time > last_abnormal_stop_time and \
            last_normal_stop_time > last_pause_time and \
            last_normal_stop_time != default_start_time and \
            last_normal_stop_time > last_check_time:
        return 'Normal_stop', datetime.now()
    elif last_abnormal_stop_time > last_normal_stop_time and \
            last_abnormal_stop_time > last_pause_time and \
            last_abnormal_stop_time != default_start_time and \
            last_abnormal_stop_time > last_check_time:
        return 'Abnormal_stop', datetime.now()
    elif last_pause_time > last_normal_stop_time and \
            last_pause_time > last_abnormal_stop_time and \
            last_pause_time != default_start_time and \
            last_pause_time > last_check_time:
        return 'Pause_stop', datetime.now()

    else:
        return 'Null', datetime.now()


def enumHandler2(hwnd, lParam):
    global LOOKUP_WINDOW_HWND
    if win32gui.IsWindowVisible(hwnd):
        wintitle = win32gui.GetWindowText(hwnd)
        if wintitle.find(LOOKUP_WINDOW_TEXT) >= 0:
            print(wintitle)
            LOOKUP_WINDOW_HWND = hwnd


# checking score():
def checking_score(player_id, max_win, already_won, last_status):
    global default_start_time, last_time, LOOKUP_WINDOW_TEXT, LOOKUP_WINDOW_HWND
    last_win = last_status[0]
    last_losses = last_status[1]
    last_concedes = last_status[2]
    logging.info('start to check the failure')

    # first the check if the hearth still there
    LOOKUP_WINDOW_TEXT = '炉石传说'
    LOOKUP_WINDOW_HWND = 0
    win32gui.EnumWindows(enumHandler2, None)
    if LOOKUP_WINDOW_HWND == 0:
        logging.warning('player No.' + str(player_id) + ' crashed! -- not hearthstone window found!')
        print('game crashed, no hearthstone windows found!')
        return 999, 999, 999

    # checking if bot stopped
    default_start_time = datetime.combine(datetime.today().date(), datetime.min.time())
    result, last_time = check_bot_stopped(log_file, default_start_time, last_time)

    if result == 'Normal_stop':
        logging.warning('player No.' + str(player_id) + ' got 32 wins!')
        logging.info('close hstone program.....')
        kill_process('Hearthstone.exe', '炉石传说')
        kill_process('Battle.net.exe', '暴雪战网')
        return 99, 99, 99
    elif result == 'Abnormal_stop':
        logging.warning('player No.' + str(player_id) + ' crashed!')
        print('%s at last checking time of %s' % (str(result), str(last_time)))
        return 999, 999, 999
    elif result == 'Pause_stop':
        print('%s at last checking time of %s' % (str(result), str(last_time)))
        logging.warning('player No.' + str(player_id) + ' paused')
        return 88, 88, 88
    else:
        last_losses += 1
        return last_win, last_losses, last_concedes



# checking failure
def checking_failure():
    global already_won, player_break, general_failure

    if general_failure == 'STALK!':
        print('failure found !')
        logging.warning('failure found')
        logging.warning('game disconnected.....')
        logging.warning('close hstone program.....')
        kill_process('Hearthstone.exe', '炉石传说')
        kill_process('Battle.net.exe', '暴雪战网')
        player_break += 1
        logging.info('adding one more failure...')
        general_failure = 'NORMAL'
        return True
    return False


def move_and_click(position, ta=0.4, tb=0.6):
    time.sleep(random.uniform(ta, tb))
    pyautogui.moveTo(position[0], position[1], 1, pyautogui.easeInQuad)
    time.sleep(random.uniform(ta, tb))
    pyautogui.click()


#  gold_miner_loop for single acc:
def gold_miner_loop(acc):
    global player_id, player_break, already_won, general_failure, need_to_reset_counter, last_status
    if acc['max'] <= acc['won']:
        print('current_id should have max %s wins..' % str(acc['max']))
        print('it has alread won %s times..' % str(acc['won']))
        player_id += 1
        player_break = 0
        already_won = 0
        logging.info('shift to the next player...')
        if player_id >= total_account:
            logging.warning('maxium players has been played....terminating...')
            kill_process('Hearthstone.exe', '炉石传说')
            kill_process('Battle.net.exe', '暴雪战网')
            return True
        return False

    if (not is_not_midnight() and not auto_start) or \
            (is_not_midnight() >= 80000 and not auto_start):
        logging.warning('midnight is coming, start the standard farming')
        kill_process('Hearthstone.exe', '炉石传说')
        kill_process('Battle.net.exe', '暴雪战网')
        time.sleep(600)  # in case relog in the same round
        return True

    # log in hs according to account id
    hs_window = log_in_hs(acc)
    time.sleep(3)
    initialize_hs_window(hs_window)

    # close bt window be set in configuration of bn / set in bt configuration file
    kill_process('Battle.net.exe', '暴雪战网')
    time.sleep(15)
    logging.info('battle net window was auto_shut!')

    load_and_initiate_ranger()

    if need_to_reset_counter:
        reset_status()
        need_to_reset_counter = False

    start_ranger()
    t = time.time()
    checking_continue = True
    checking_period = 180  # check in every 10 minutes

    while checking_continue:
        time.sleep(3)

        if time.time() - t >= checking_period - 10:
            if (not is_not_midnight() and not auto_start) or \
                    (is_not_midnight() >= 80000 and not auto_start):
                logging.warning('midnight is coming, start the standard farming')
                kill_process('Hearthstone.exe', '炉石传说')
                kill_process('Battle.net.exe', '暴雪战网')
                time.sleep(600)  # in case relog in the same round
                return True
            last_status = checking_score(player_id, acc['max'] - acc['won'], already_won, last_status)
            print(last_status)
            if last_status == (99, 99, 99):  # normal finished
                player_id += 1
                player_break = 0
                already_won = 0
                need_to_reset_counter = True
                logging.info('shift to the next player...')
                if player_id >= total_account:
                    logging.warning('maxium players has been played....terminating...')
                    kill_process('Hearthstone.exe', '炉石传说')
                    kill_process('Battle.net.exe', '暴雪战网')
                    return True
                break
            elif last_status == (999, 999, 999):
                general_failure = 'STALK!'
            elif last_status == (88, 88, 88):
                start_ranger()
                last_status = (0, 0, 0)
                pass
            checking_continue = not checking_failure()
            t = time.time()
    return False


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
                time.sleep(2)
                break
        win32gui.SetForegroundWindow(hwndbnt)
        time.sleep(0.5)
        return hwndbnt

    # login process
    def login(self):
        # to log in id
        # should check size ration of the login window of btnet. Normal 4, other 5  ********************
        pyautogui.keyDown('shift')
        time.sleep(0.2)
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.keyUp('shift')
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


# ------------------------- initialization I ---------------------------------------------------------------------------
logging.basicConfig(filename='ranger_running_' + str(datetime.now().date()) + '.log', filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y--%H:%M:%S', level=logging.DEBUG)
logging.info('Program starts.')

# checking capslock is not activated.
while GetKeyState(VK_CAPITAL):
    pyautogui.press('capslock')
    logging.info('capslock released!')

# --------------------------variables------------------------------------------------
bn_target = winshell.shortcut(os.path.join(winshell.desktop(), "暴雪战网.lnk")).path
hs_target = winshell.shortcut(os.path.join(winshell.desktop(), "炉石传说.lnk")).path

logging.warning('ranger switcher running!')


ranger_btn_dict = {'start_btn': (368, 267),
                   'config_btn': (100, 260),
                   'auto_stop_sheet': (1300, 115),
                   'reset_win_counter_btn': (945, 370),
                   'save_config_btn': (1250, 1035)}

ranger_txt = ''
ranger_hwnd = 0
last_status = (0, 0, 0)
# log_file = 'c:\\HearthRanger\\task_log\\test\\*.log'
log_file = '*.log'
LOOKUP_WINDOW_TEXT = '炉石传说'
LOOKUP_WINDOW_HWND = 0
default_start_time = datetime.combine(datetime.today().date(), datetime.min.time())
last_time = default_start_time
general_failure = 'NORMAL'  # NORMAL means no failure

# # -------------------------- initializaion II-----------------------------------------
# deleting old log files
clean_log_files()
logging.warning('OLD LOG FILES DELETED!')

# get standard farming list in to sf_list
generate_farming_list('account_per.txt', 'acc_farm_list.pcl')
sf_list = parse_farming_list_file('acc_farm_list.pcl')

# sf_list format as following:
# [{'acc': account_id[i], 'psw': account_psd[i], 'max': max_wins[i], 'won': already_won[i], 'dck': deck_list[0]}, ..]

total_account = len(sf_list)

auto_start = wait_for_midnight()

if not auto_start:
    # get today's farming order from a user
    tf_list = get_and_parse_command()
    for i in tf_list:
        print(i)
    time.sleep(1)
    # so far we have tf_list to start farming and sf_list for the next day.
    logging.info('standard_farming list and today_farming list all loaded!')
else:
    tf_list = []

# if it is an instant command, start to farm right now:
if tf_list != []:
    print('temp_farming list as following..:', file=sys.stderr)
    time.sleep(0.4)
    print(tf_list)
    player_id = 0
    player_break = 0
    need_to_reset_counter = True
    already_won = 0
    acc = tf_list[player_id]
    total_account = len(tf_list)
    while player_id <= total_account:
        print('current No. %s account detail: ' % str(player_id), end='')
        print(acc)
        farm_done = gold_miner_loop(acc)
        if farm_done:
            break
        acc = tf_list[player_id]

    print('temp farming ended!', file=sys.stderr)
    time.sleep(0.4)
    auto_start = wait_for_midnight()

# midnight farm loop
total_account = len(sf_list)
auto_start = True

while True:
    player_id = 0
    player_break = 0
    already_won = 0
    need_to_reset_counter = True
    acc = sf_list[player_id]
    print('standard_farming list as following..:', file=sys.stderr)
    time.sleep(0.4)
    print(sf_list)
    while player_id <= total_account:
        print('current No. %s account detail: ' % str(player_id), end='')
        print(acc)
        farm_done = gold_miner_loop(acc)
        if farm_done:
            break
        acc = sf_list[player_id]

    auto_start = wait_for_midnight()

# --------------------------main loop starts here-----------------------------------------------------------------------


