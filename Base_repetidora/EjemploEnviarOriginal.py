from network import WLAN
import socket
import select
import time

#Setup WiFi AP
wlan = WLAN(mode=WLAN.AP,
            ssid='Gateway1',
            auth=(WLAN.WPA2,'password'),
            antenna=WLAN.INT_ANT)


# Bind to the port
port = 12345
s = socket.socket()
s.bind(socket.getaddrinfo("0.0.0.0", port)[0][4])
s.listen(1)

print("Running server")
while True:
    readable, writable, errored = select.select([s], [], [])

    for s in readable:
        cl, remote_addr = s.accept()
        cl.setblocking(True)
        print("Client connection from:", remote_addr)

        file = "/flash/test.txt"
        print("Sending: ", file)

        with open(file, 'rb') as f:
            data = f.read(1024)
            while(data):
                print("sending", data)
                cl.sendall(data)
                data = f.read(1024)
        print("Done Sending")
        cl.close()
