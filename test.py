import json
with open('account_per_3.0.json', 'r') as data:
    acc_list = json.load(data)

print(acc_list[0]['acc'], acc_list[0]['psw'])

