from network import WLAN
import socket
import select
import machine
import time

# Connect to server AP
wlan = WLAN(mode=WLAN.STA)
nets = wlan.scan()
for net in nets:
    if net.ssid == 'Gateway1':
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, 'password'), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break
else:
    raise Exception("WiFi network not found")

# sleep just to make sure the wifi is connected
time.sleep(1)

ip, subnet, gateway, dns = wlan.ifconfig()
print("wlan->",wlan.ifconfig())
# Connect to server
port = 12345
s = socket.socket()
print("g->",gateway)
print("Connecting to: ", gateway, port)
s.connect((gateway, port))
s.setblocking(True)
s.settimeout(2)

file = "/flash/testeando.txt"
print("Sending: ", file)

with open(file, 'rb') as f:
    data = f.read(1024)
    while(data):
        print("sending", data)
        s.sendall(data)
        data = f.read(1024)
print("Done Sending")
s.close()
wlan.disconnect()
