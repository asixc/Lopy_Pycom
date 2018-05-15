#Prueba de boot.py :
import machine
import math
import network
import os
import time
import utime
import pycom
from machine import RTC
from machine import SD
from machine import Timer
from L76GNSS import L76GNSS
from pytrack import Pytrack
# setup LoRa:
from network import LoRa
import socket
lora = LoRa(mode=LoRa.LORA)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# setup as a station
import gc
time.sleep(2)
gc.enable()

def existe(arg):
    try:
        fichero = open(arg)
        fichero.close()
        return True
    except:
        return False

def pulsaciones(color):
    for x in range(3):
        pycom.rgbled(color)
        time.sleep(0.1)
        pycom.heartbeat(False)
        time.sleep(0.1)


def ConfirmacionLed(funcion):
    funciones={'bluetooth':0x0007F,'gpsok':0xfffe02,'nogps':0x7f0000,'encendido':0x7f700,'sendalert':0xC011EB,'buscandoalerta':0xffffff}
    pulsaciones(funciones[funcion])

def buscarMensajes():
    for x in range(10):
        alertas=[]
        s.setblocking(False)
        data = s.recv(128)
        ide =data.decode("utf-8")
        ide = ide.split('-')
        if ide[0] == 'alerta':
            ConfirmacionLed('sendalert')
            if ide[1] not in alertas:
                alertas.append(ide[1])
                ConfirmacionLed('bluetooth')
                f = open ('alerta.txt', 'w')
                f.write(ide[1])
                f.close()
        elif ide[0] == 'seguidores':
            tmp = ide[1]
            ide = ide[1].split(';')
            if ide[0]==dorsal:
                ConfirmacionLed('bluetooth')
                f = open ('seguidores.txt', 'w')#Modo 'a' Para a�adir no sobre escribir
                f.write(tmp)
                f.close()
        time.sleep(3)

# setup rtc
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
#print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
#print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')
py = Pytrack()
l76 = L76GNSS(py, timeout=30)
chrono = Timer.Chrono()
chrono.start()

pycom.heartbeat(False)
ConfirmacionLed('encendido')

j=0
nintentos = 0
pycom.heartbeat(False)
while (True):
    s.setblocking(True)
    coord = l76.coordinates()
    if existe('dorsal.txt'):
        a = open('dorsal.txt')
        dorsal = a.read()
        x = "witeklab-"+str(j)+"-"+str(dorsal)+"-"+str(coord[0]) + "-"+str(coord[1])
    else:
        x = "witeklab-"+str(j)+"-"+"null-"+str(coord[0]) + "-"+str(coord[1])

    p = str(coord[0])
    if p =='None':
        ConfirmacionLed('nogps')
        nintentos+=1
    else:
        s.send(x)
        ConfirmacionLed('gpsok')
        j+=1
        time.sleep(20) #Pausa entre toma de coordenadas.

    ConfirmacionLed('buscandoalerta')
    buscarMensajes()
