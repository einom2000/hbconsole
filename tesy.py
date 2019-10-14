import win32gui
import win32process
import re
import keyboard
import pyautogui
import time
import os
import glob
from datetime import datetime


def time_differ(time1, time2):
    duration_seconds_in_total = (time1 - time2).total_seconds()
    duration_hours = duration_seconds_in_total // 3600
    duration_minutes = (duration_seconds_in_total % 3600) // 60
    return duration_hours, duration_hours


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


# ============= find the last normal exit ================= 'Bot stopped'==========
# as well as find the last abnormal stop
def check_bot_stopped(file, last_checking_time=datetime.today().date()):
    format = '%H:%M:%S'
    print(last_checking_time)
    newest_stop_log = max(glob.iglob(file), key=os.path.getctime)   #'c:\\HearthRanger\\task_log\\test\\*.log'

    last_normal_stop = ''
    previous_line = ''
    last_abnormal_stop = ''
    last_pause = ''

    for line in reversed(open(newest_stop_log, encoding='utf-8').readlines()):
        if line.find('Bot stopped.') >= 0:
            previous_line = 'Bot stopped.'
        elif previous_line == 'Bot stopped.' and \
                line.find('Game client closed by CloseGameAfterAutoStopped settings.') >= 0 and \
                last_normal_stop == '':
                    last_normal_stop = line.strip()[0:line.find('INFO') - 1]
                    if last_abnormal_stop != '':
                        break
        elif previous_line == 'Bot stopped.' and \
                line.find('Game client closed by CloseGameAfterAutoStopped settings.') < 0  and \
                last_abnormal_stop == '':
                    last_abnormal_stop = line.strip()[0:line.find('INFO') - 1]
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
        last_normal_stop_time = 0
    if last_abnormal_stop != '':
        last_abnormal_stop_time = datetime.combine(datetime.now().date(),
                                                   datetime.strptime(last_abnormal_stop, format).time())
        print('Game client last abnormal stoped at :', end='')
        print(last_abnormal_stop_time)
    else:
        last_abnormal_stop_time = 0

    # return checking result
    if last_normal_stop_time >= last_abnormal_stop_time:
        return 'Normal_stop', datetime.now()




# log_file = 'c:\\HearthRanger\\task_log\\test\\*.log'
log_file = '*.log'
result, last_check_time = check_bot_stopped(log_file)
print('%s at last checking time of %s' %(str(result), str(last_check_time)))
# ================================= check the last bot abnormal stopped ===


