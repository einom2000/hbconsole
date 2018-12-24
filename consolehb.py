import  os, pyautogui,keyboard, win32gui,win32api
# tsks = os.popen('tasklist').readlines()
# for tsk in tsks:
#     if 'Battle.net' in tsk:
#         print(tsk)
#         print ("yes!")

while True:
    if keyboard.is_pressed('space'):
        # print(pyautogui.position())
        print(win32api.GetKeyboardLayout())
