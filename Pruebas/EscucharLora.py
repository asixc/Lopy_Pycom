#Generado el 10-09-2018
from network import LoRa
import time
import os
import pycom
import _thread

lora = LoRa(mode=LoRa.LORA)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

while True:
    try:
        s.setblocking(True)
        data = s.recv(128)
        print("Mensaje recibido:",data)
    except:
        print('Algo ha fallado')
