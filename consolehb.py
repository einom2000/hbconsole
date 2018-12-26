import  os, pyautogui,keyboard, win32gui,win32api, winshell, psutil,time,random
# tsks = os.popen('tasklist').readlines()
# for tsk in tsks:
#     if 'Battle.net' in tsk:
#         print(tsk)
#         print ("yes!")
#
# while True:
#     if keyboard.is_pressed('space'):
#         hwnd = win32gui.GetForegroundWindow()
#         txt = win32gui.GetWindowText(hwnd)
#         print(txt)

# def kill_process(process_name, wd_name):
#     for proc in psutil.process_iter():
#         print(proc)
#         # check whether the process name matches
#         if proc.name() == process_name:
#             proc.kill()
#     return
# #
# bn_target = winshell.shortcut(os.path.join(winshell.desktop(), "暴雪战网.lnk")).path
# print(bn_target)
# bn = 'Battle.net.exe'
# print(bn)
# print("try to kill")
# kill_process(bn, '暴雪战网登录')
# f = open("account.txt", "r")
# lines = f.readlines()
# account_id = (lines[0][:-1], lines[2][:-1], lines[4][:-1])
# account_psd = (lines[1][:-1], lines[3][:-1], lines[5][:-1])
# f.close()
# print(account_id,accoun t_psd)

# (915, 259)(1108, 333)  (1231, 33)(1267, 69)
#
# while True:
#     if keyboard.is_pressed('space'):
#         print(pyautogui.position())
#         break

import json

def kill_process(process_name, wd_name):
    for proc in psutil.process_iter():
        # check whether the process name matches
        # print(proc)
        if proc.name() == process_name:
            proc.kill()
    while win32gui.FindWindow(None, wd_name):
         pass
    return

with open("Stats.json") as json_file:
    json_data = json.load(json_file)
    win_count = json_data['Wins']
    print(win_count)


kill_process('Hearthstone.exe', '炉石传说')