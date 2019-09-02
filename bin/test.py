import client_sending
import json

text = '{"bot_hears": "pause", "pet_train": "pause"}'


client_sending.sending(text, False)

data = client_sending.get(False)

with open('bin\\command.json', 'wb') as f:
    f.write(data)

