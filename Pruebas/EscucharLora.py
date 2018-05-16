#Generado el 10-09-2018
from network import LoRa
import time
import os
import pycom
import _thread

lora = LoRa(mode=LoRa.LORA)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

def escuchar(hora):
    while True:
        try:
            s.setblocking(True)
            data = s.recv(128)
            print("Mensaje recibido:",data," Hora:"+hora)
        except:
            print('Algo ha fallado')

def cronos():


def main():
    hora = time.time()
    escuchar(hora)
    cronos()
