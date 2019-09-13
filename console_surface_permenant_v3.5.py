# check json twice to compare the failure
# use the list to locate in center
# ---------------above is v3.0 -------------------------------------------

# -----------------v3.5 version ------------------------------------------
# real_time checking online command
# /bin/command.json   not encrypted dictionary for command
# /bin/en.bin  encrypted dictionary with server public key, ready for sending
# /bin/keys_here.json keys of local private, server public, and local public, all non-encrypted
# /bin/server_ip.json store non-encrypted server address and port

# deleting all logging files which are 3 days ago                                                                --check
# to check size ration of the login window of btnet. Normal 4, other 5 tabs added, before key in.
# auto check midnight time to restart                                                                            --check

# command 'pause' for quit and game and record the wins, and waiting for command'activated'
# command 'activated' resume the farming
# command 'cease' for stopping farming and wait for next day loop
# command 'quit' for quiting farming program.

# while start program, key in number required: 0 for all accounts, 23 for 2nd and 3rd account,                   --check
# 2 for 2nd account only, etc.                                                                                   --check
# changing order fo the role for the farming list forever                                                        --check

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
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".log") and file.startswith("running_2"):
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
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == process_name:
            proc.kill()
            break
    while win32gui.FindWindow(None, wd_name):
        pass
    return


# check hs folder   ------------ mono.dll and bnl_checkout_client.dll
def check_version():
    mono_path = os.path.split(hs_target)[0] + '\\Hearthstone_Data\\mono'
    target_mono_path = os.path.split(hs_target)[0] + '\\Hearthstone_Data\\mono\\etc'
    plugin_path = os.path.split(hs_target)[0] + '\\Hearthstone_Data\\plugins'
    # should be 2115520 not 2117056
    if os.path.isfile(os.path.join(mono_path, 'mono.dll')) and \
            os.path.getsize(os.path.join(mono_path, 'mono.dll')) != 2115520:
        shutil.move(os.path.join(mono_path, 'mono.dll'), os.path.join(target_mono_path, 'mono.dll'))
        print('move mono.dll to etc folder!', file=sys.stderr)
    if os.path.isfile(os.path.join(mono_path, 'MonoPosixHelper.dll')):
        shutil.move(os.path.join(mono_path, 'MonoPosixHelper.dll'),
                    os.path.join(target_mono_path, 'MonoPosixHelper.dll'))
        print('move MonoPosixHelper.dll to etc folder!', file=sys.stderr)
    if not os.path.isfile(os.path.join(mono_path, 'mono.dll')):
        shutil.copy(os.path.split(hs_target)[0] + '\\Hearthstone_Data\\mono.dll',
                    os.path.join(mono_path, 'mono.dll'))
        print('copy the 2066kb mono.dll to mono folder!', file=sys.stderr)
    if os.path.isfile(os.path.join(plugin_path, 'bnl_checkout_client.dll')):
        shutil.move(os.path.join(plugin_path, 'bnl_checkout_client.dll'),
                    os.path.join(target_mono_path, 'bnl_checkout_client.dll'))
        print('move the bnl_checkout_client.dll to etc folder.', file=sys.stderr)


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
    hs_png = 'hs' + suffix + '.png'
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
    login_png = 'login' + suffix + '.png'
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


# adjust the hs window and click away the lost_game confirmation button
# ***** select deck and style and mounting in future
def initialize_hs_window(hs_window):
    win32gui.SetForegroundWindow(hs_window)
    win32gui.MoveWindow(hs_window, 620, 0, 800, 600, 1)  # (90, 420)
    t = time.time()
    # (986, 355), (1055, 389)
    move_and_click((739 + re_x, 116 + re_y))
    time.sleep(10)
    hs_rec = win32gui.GetWindowRect(hs_window)
    print('found hs_window at %s!' % str(hs_rec), sys.stderr)
    # if there is a lost game button, click it
    while time.time() - t <= 20:
        lost_confirm = pyautogui.locateCenterOnScreen('lost_confirmation_logo_new.png',
                                                      region=(950 + re_x, 300 + re_y, 400, 200),
                                                      grayscale=False, confidence=0.6)
        if lost_confirm is not None:

            move_and_click((1000 + re_x, 375 + re_y))
            logging.warning('last game was lost! click to confirm!')
            break

    # click away the mission panels
    move_and_click((739 + re_x, 116 + re_y))
    # here could add picking deck order and game style and farming or mounting in future
    t = time.time()
    while time.time() - t <= 20:
        found_btn = pyautogui.locateCenterOnScreen(start_battle_button_png,
                                                   region=HS_START_BATTLE_BTN_REGION,
                                                   grayscale=False, confidence=0.7)
        if found_btn is not None:

            move_and_click((HS_START_BATTLE_BTN_REGION[0] + 100, HS_START_BATTLE_BTN_REGION[1] + 30))
            logging.warning('into battle mode!')
            break



# load buddy
def load_and_initiate_buddy():
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
    click_hb_btn(buddy_btn_dict['setting_btn'])
    click_hb_btn(buddy_btn_dict['default_bot_btn'])
    click_hb_btn(buddy_btn_dict['deck_btn'])
    # uncheck 2 boxes for cache. It is a hard code!
    move_and_click((367, 445))
    time.sleep(2)
    move_and_click((371, 488))
    time.sleep(2)
    logging.info('buddy was initiated!')


# select enter battle and select deck, if any
def start_hs_first_game_round():
    # FOR UPDATE FROM APRIL 5TH MONO.DLL WAS RE-ALLOCATED
    # *** if want to check the deck, add here

    # select the deck
    move_and_click(HS_ROW1_COLUMN1_DECK_BUTTON_AFTER_REVISED)

    # select the casual farming
    move_and_click(HS_CASUAL_FARMING_BUTTON_AFTER_REVISED)
    print('starting first game round..')
    while True:
        move_and_click(HS_BATTLE_SELECTION_BTN, ta=1.0, tb=2.0)
        if start_new_round():
            return


# start a new round
def start_new_round():
    global buddy_status
    found_it = pyautogui.locateCenterOnScreen('START_NEW.png', region=HS_START_BTN_REGION,
                                              grayscale=False, confidence=0.7)
    if found_it is not None:
        print('found START button as %s' % str(found_it))

        # check if the buddy is still starting
        buddy_status = check_buddystatus()
        if buddy_status:
            start_buddy_round()

        print('checking if it is in wild mode?')
        found_wild = pyautogui.locateCenterOnScreen(wild_logo_png, region=HS_WILD_BOX_AFTER_REVISED,
                                                  grayscale=False, confidence=0.8)
        if found_wild:
            move_and_click(HS_WILD_BOX_CLICK_AFTER_REVISED)
            time.sleep(1)

        # if you want to check the wild / standard, check it here
        move_and_click(HS_BATTLE_START_BTN)
        time.sleep(random.randint(1000, 2000) / 1000)
        t = time.time()
        while time.time() - t <= 30:
            time.sleep(2)
            if pyautogui.locateCenterOnScreen('searching_new.png', region=SEARCHING_BOX,
                                              grayscale=False, confidence=0.7) is not None:
                buddy_status = check_buddystatus()
                if not buddy_status:
                    start_buddy_round()
                return True
        return True
    return False


def check_buddystatus():
    if pyautogui.locateCenterOnScreen(hb_yellow_start_png, region=buddy_btn_dict['start_btn_region'],
                                      grayscale=False, confidence=0.7):
        return False
    else:
        return True


# start a new buddy round
def start_buddy_round():
    global buddy_status
    # make sure the buddy_status is correct
    click_hb_btn(buddy_btn_dict['start_btn'])
    time.sleep(3)
    if buddy_status:
        logging.info('stop the buddy.')
    if not buddy_status:
        logging.info('start the buddy.')
    time.sleep(3)
    buddy_status = not buddy_status

    # **** should check the stop button shows up


# reset buddy status
def reset_status():
    time.sleep(1)
    click_hb_btn(buddy_btn_dict['stats_btn'])
    time.sleep(1)
    click_hb_btn(buddy_btn_dict['stats_reset_btn'])
    logging.info('status info reset!')


# checking score():
def checking_score(player_id, max_win, already_won, last_status):
    last_win = last_status[0]
    last_losses = last_status[1]
    last_concedes = last_status[2]
    logging.info('start to check the score...')
    # read score
    with open("Settings\Default\Stats.json") as json_file:
        json_data = json.load(json_file)
        print('jsondata = ')
        print(json_data)
        logging.info('status shows: ' + str(json_data))
        win_count = json_data['Wins']
        lose_count = json_data['Losses']
        concede_count = json_data['Concedes']
        if int(win_count) >= (max_win - already_won):
            logging.warning('player No.' + str(player_id) + ' got ' + str(win_count + already_won) + ' wins!')
            logging.info('close hstone program.....')
            kill_process('Hearthstone.exe', '炉石传说')
            return 99, 99, 99
        if int(win_count) == last_win and int(lose_count) == last_losses and \
                int(concede_count) == last_concedes:
            print('here is no changed score during last 15 minutes, restarting....')
            return 999, 999, 999
        else:
            return int(win_count), int(lose_count), int(concede_count)


# checking failure
def checking_failure():
    global already_won, player_break, general_failure

    for failure in failure_checking_list:
        print('checking failure..' + str(failure))
        failure_found = pyautogui.locateCenterOnScreen(failure[0], region=failure[1],
                                                       grayscale=False, confidence=0.7)
        if failure_found is not None or general_failure == 'STALK':
            print('failure found !' + str(failure))
            logging.warning('failure found' + str(failure))
            logging.warning('game disconnected.....')
            with open("Settings\Default\Stats.json") as json_file:
                json_data = json.load(json_file)
                logging.info('status shows: ' + str(json_data))
                win_count = json_data['Wins']
                already_won += int(win_count)
            logging.warning(str(acc['acc']) + ' fails ' + str(player_break) + ' times!')
            logging.warning('Player won ' + str(already_won) + ' games before broken!')
            time.sleep(60)
            logging.warning('close hstone program.....')
            kill_process('Hearthstone.exe', '炉石传说')
            player_break += 1
            logging.info('adding one more failure...')
            return True
    return False


def move_and_click(position, ta=0.4, tb=0.6):
    time.sleep(random.uniform(ta, tb))
    pyautogui.moveTo(position[0], position[1], 1, pyautogui.easeInQuad)
    time.sleep(random.uniform(ta, tb))
    pyautogui.click()


#  gold_miner_loop for single acc:
def gold_miner_loop(acc):
    global player_id, player_break, already_won, general_failure
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
            return True
        return False

    if (not is_not_midnight() and not auto_start) or \
            (is_not_midnight() >= 80000 and not auto_start):
        logging.warning('midnight is coming, start the standard farming')
        kill_process('Hearthstone.exe', '炉石传说')
        time.sleep(600)  # in case relog in the same round
        return True

    # log in hs according to account id
    hs_window = log_in_hs(acc)
    time.sleep(3)
    initialize_hs_window(hs_window)

    # close bt window be set in configuration of bn / set in bt configuration file
    # kill_process('Battle.net.exe', '暴雪战网')
    time.sleep(15)
    logging.info('battle net window was auto_shut!')

    load_and_initiate_buddy()
    start_hs_first_game_round()

    # just click to focus the hs window
    move_and_click((850 + re_x, 200 + re_y))

    reset_status()
    last_status = (0, 0, 0)  # last_win , last_losses, last_concedes = 0, 0, 0

    t = time.time()
    checking_continue = True
    checking_period = 180  # check in every 15 minutes

    while checking_continue:
        time.sleep(3)
        # check if the round is ended, if yes start a new one
        ct = time.time()
        while not start_new_round():
            if time.time() - ct >= 60:
                break
            pass

        if time.time() - t >= checking_period - 10:
            move_and_click((850 + re_x, 200 + re_y))
            if (not is_not_midnight() and not auto_start) or \
                    (is_not_midnight() >= 80000 and not auto_start):
                logging.warning('midnight is coming, start the standard farming')
                kill_process('Hearthstone.exe', '炉石传说')
                time.sleep(600)  # in case relog in the same round
                return True
            last_status = checking_score(player_id, acc['max'] - acc['won'], already_won, last_status)
            print(last_status)
            if last_status == (99, 99, 99):  # normal finished
                player_id += 1
                player_break = 0
                already_won = 0
                logging.info('shift to the next player...')
                if player_id >= total_account:
                    logging.warning('maxium players has been played....terminating...')
                    kill_process('Hearthstone.exe', '炉石传说')
                    return True
                break
            elif last_status == (999, 999, 999):
                general_failure = 'STALK!'
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
        self.normalSize = True

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
                # check the abnormal size of login window
                rec = win32gui.GetWindowRect(hwndbnt)
                if len(rec) > 3:
                    w = rec[2] - rec[0]
                    h = rec[3] - rec[1]
                    if w > STANDARD_BNT_SIZE_SUR[0] and h > STANDARD_BNT_SIZE_SUR[1]:
                        self.normalSize = False
                    else:
                        self.normalSize = True
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
logging.basicConfig(filename='running_' + str(datetime.now().date()) + '.log', filemode='a',
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

if os.path.basename(__file__) == 'console_surface_permenant_v3.5.py':
    logging.warning('script running on surface with an endless loop!')
    suffix = '_sur'
else:
    suffix = ''
    logging.warning('script running on other machine with an endless loop!')
logging.info('All variables were loaded.')

# if suffix == "_sur":
buddy_btn_dict = {'start_btn': (366, 180),
                  'setting_btn': (175, 236),
                  'default_bot_btn': (175, 279),
                  'mode_btn': (477, 608),
                  'rule_btn': (479, 653),
                  'deck_btn': (354, 697),
                  'stats_btn': (459, 278),
                  'stats_reset_btn': (83, 456),
                  'win_rec': [(84, 174), (116, 197)],
                  'start_btn_region': (320, 160, 90, 40)}
# revised x and y
re_x = 90
re_y = 420
buddy_status = False
general_failure = 'NORMAL'

HS_BATTLE_SELECTION_BTN = (1017 + re_x, 218 + re_y)
HS_BATTLE_START_BTN = (1239 + re_x, 487 + re_y)
HS_START_BTN_REGION = (1000 + re_x, 300 + re_y, 500, 500)
SEARCHING_BOX = (900 + re_x, 100 + re_y, 400, 300)

# version 3.5 and above new checking position
STANDARD_BNT_SIZE_SUR = (370, 550)
HS_WILD_BOX_AFTER_REVISED = (1280, 470, 60, 50)
HS_WILD_BOX_CLICK_AFTER_REVISED = (1310, 495)
HS_ROW1_COLUMN1_DECK_BUTTON_AFTER_REVISED = (1080, 610)
HS_CASUAL_FARMING_BUTTON_AFTER_REVISED = (1250, 570)
HS_START_BATTLE_BTN_REGION = (1000, 600, 200, 60)
HS_SHUT_REGION =(970, 670, 200, 100)
wild_logo_png = 'wild_logo' + suffix + '.png'
hb_dart_start_png = 'hb_dark_start_sur.png'
hb_yellow_start_png = 'hb_yellow_start_sur.png'
hb_yellow_stop_png = 'hb_yellow_stop_sur.png'
start_battle_button_png = 'hs_start_btn_sur.png'
shut_down_png = 'hs_shut_sur.png'
break4_rgn = (900, 690, 100, 100)
break4_png = 'shock_mark_sur.png'
BNT_MAINTAIN_LOGO_REGION = (110, 110, 250, 200)
bt_maintain_logo = 'bt_maintain_logo_sur.png'
#----new variables end here

wild_logo_rgn = (1220 + re_x, 45 + re_y, 1270, 90)
close_logo_png = 'close_logo' + suffix + '.png'
close_logo_rgn = (900 + re_x, 200 + re_y, 1300, 500)
break1_png = 'broke1' + suffix + '.png'
break2_png = 'broke2' + suffix + '.png'
break3_png = 'broke3' + suffix + '.png'
break1_rgn = (750 + re_x, 260 + re_y, 840, 350)
break2_rgn = (890 + re_x, 240 + re_y, 1160, 400)
break3_rgn = (890 + re_x, 240 + re_y, 1160, 400)

failure_checking_list = [(close_logo_png, close_logo_rgn),
                         (shut_down_png, HS_SHUT_REGION),
                         (break2_png, break2_rgn),
                         (break3_png, break3_rgn),
                         (break4_png, break4_rgn)]

# -------------------------- initializaion II-----------------------------------------
# deleting old log files
clean_log_files()
logging.warning('OLD LOG FILES DELETED!')

# check version of hs
check_version()
logging.warning('checking hs version completed.')

# get standard farming list in to sf_list
generate_farming_list('account_per.txt', 'acc_farm_list.pcl')
sf_list = parse_farming_list_file('acc_farm_list.pcl')

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


