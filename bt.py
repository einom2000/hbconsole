import sys
import bluetooth, serial

bd_addr = 'a3:3a:11:04:0d:5d'
send_port = 11
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((bd_addr, send_port))
sock.send('o')