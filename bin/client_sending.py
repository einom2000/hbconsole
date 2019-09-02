
import communication
import json
import rsa_encrypto


def sending(text, show_detail):
    en_file = 'bin\\en.bin'
    key_file = 'bin\\keys_here.json'
    server_file = 'bin\\server_ip.json'
    with open(key_file) as f:
        keys = json.load(f)

    recipient_pub = keys['SERVER_PUB']

    rsa_encrypto.encryption(text, recipient_pub, en_file)

    with open(en_file, 'rb') as f:
        data = f.read()

    with open(server_file) as f:
        server = json.load(f)

    server_address = (server['server_ip'], server['server_port'])

    sock = communication.sock()

    communication.connect(sock, server_address)

    communication.send(sock, b'SEND', show_detail)
    response = communication.check_response(sock, b'OK', b'READY?', 128)
    if response == 1:
        communication.send(sock, data, show_detail)
        communication.close(sock)
        return None
    if response == 2:
        data = communication.receiving_data(sock, 1024)
        communication.close(sock)
        return data


def get(show_detail):

    server_file = 'bin\\server_ip.json'

    with open(server_file) as f:
        server = json.load(f)
    server_address = (server['server_ip'], server['server_port'])

    sock = communication.sock()

    communication.connect(sock, server_address)

    communication.send(sock, b'GET', show_detail)
    response = communication.check_response(sock, b'OK', b'READY?', 128)
    if response == 2:
        data = communication.receiving_data(sock, 1024)
        communication.close(sock)
        return data

def main():
    pass


if __name__ == '__main()__':
    main()


