import win32gui
import win32process

def enumHandler(hwnd, lParam):
    global wintitle
    if win32gui.IsWindowVisible(hwnd):
        wintitle = win32gui.GetWindowText(hwnd)
        # if len(wintitle) > 0:
        #     print(win32gui.GetWindowText(hwnd), end=' ----->  ')
        #     _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        #     print(r'pid = %s' % str(found_pid))
        #     print(r'hwnd= %s' % str(hwnd))

win32gui.EnumWindows(enumHandler, None)

keyword = ['ycharm', '炉石', '暴雪', '设置', 'Program']
for key in keyword:
    if not wintitle.rfind(key):
        print(wintitle)
        break