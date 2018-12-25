import  os, pyautogui,keyboard, win32gui,win32api, winshell, psutil
# tsks = os.popen('tasklist').readlines()
# for tsk in tsks:
#     if 'Battle.net' in tsk:
#         print(tsk)
#         print ("yes!")

# while True:
#     if keyboard.is_pressed('space'):
#         hwnd = win32gui.GetForegroundWindow()
#         txt = win32gui.GetWindowText(hwnd)
#         print(txt)

def kill_process(process_name, wd_name):
    for proc in psutil.process_iter():
        print(proc)
        # check whether the process name matches
        if proc.name() == process_name:
            proc.kill()
    return

bn_target = winshell.shortcut(os.path.join(winshell.desktop(), "暴雪战网.lnk")).path
print(bn_target)
bn = 'Battle.net.exe'
print(bn)
print("try to kill")
kill_process(bn, '暴雪战网登录')