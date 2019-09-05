# from datetime import *
# import os, sys
#
# valid_date = datetime.now() + timedelta(days=-160)
# for root, dirs, files in os.walk("C:\\Users\\Einom_Ng\\PycharmProjects\\hbconsole"):
#     for file in files:
#         if file.endswith(".log") and file.startswith("running_2"):
#             log_date = datetime.strptime(file[-14: -4], "%Y-%m-%d")
#             if log_date < valid_date:
#                 filename = os.path.join(root, file)
#                 os.remove(filename)
#                 print('Deleting OLD LOG FILE: ', file=sys.stderr)
#                 print(filename)




# filename = 'running_' + str(datetime.now().date() - 1) + '.log'

# print(filename)
# print(' 1 '.strip(' ').isdigit())


import time
from datetime import datetime

# print(time.time())
# print(datetime.now())
a = [(1,2), (2, 4)]
print(str(a))