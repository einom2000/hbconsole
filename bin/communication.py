import socket
import sys


def connect(sock, server_address):
    sock.connect(server_address)


def close(sock):
    sock.close()


def bind_listen(sock, server_address, a):
    sock.bind(server_address)
    sock.listen(a)


def sock():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def server_accept(sock):
    connection, client_address = sock.accept()
    return connection, client_address


def send(sock, msg, show_message):  #msg = b''
    try:
        message = msg
        sock.sendall(message)
        if show_message:
            print('sending %s' % message, file=sys.stderr)
        length = (len(message))
        print('send data at length of %d' % length, file=sys.stderr)
    finally:
        return


def check_response(sock, msg1, msg2, length):  # msg = b''
    while True:
        data = sock.recv(length)
        if data and data == msg1:
            print('received: %s' % data.decode('utf-8'), file=sys.stderr)
            return 1
        if data and data == msg2:
            print('received: %s' % data.decode('utf-8'), file=sys.stderr)
            return 2


def receiving_data(sock, length):
    while True:
        data = sock.recv(length)
        if data:
            length = len(data)
            print('received data at length of %d' % length)
            break
    return data

