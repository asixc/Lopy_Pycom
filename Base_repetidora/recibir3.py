from network import WLAN
import socket
import select
import time

#Setup WiFi AP
wlan = WLAN(mode=WLAN.AP,
            ssid='Gateway1',
            auth=(WLAN.WPA2,'password'),
            antenna=WLAN.INT_ANT)

def existe(fichero):
    try:
        f = open(fichero, "r")
        exists = True
        f.close()
    except:
        exists = False
    return exists


# Bind to the port
port = 12345
while True:
    s = socket.socket()
    s.bind(socket.getaddrinfo("0.0.0.0", port)[0][4])
    s.listen(1)
    print("Mostramos listado:",os.listdir())
    if existe('testeando.txt'):
        print("Mostramos contenido fichero testeando.txt:")
        print(open('testeando.txt').read())
        pass

    print("\n\nEsperando conexion")
    readable, writable, errored = select.select([s], [], [])
    for s in readable:
        cl, remote_addr = s.accept()
        cl.setblocking(True)
        cl.settimeout(2)
        print("Client connection from:", remote_addr)
        file = "/flash/testeando.txt"
        print("writing: ", file)

        with open(file, 'wb') as f:
            while True:
                try:
                    data = cl.recv(1024)
                    print(data)
                    f.write(data)
                    f.close()
                except TimeoutError:
                    break
    print("Recibido...")
    s.close()
