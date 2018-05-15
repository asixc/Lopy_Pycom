#   Revisado y actualizado el 15 de Mayo de 2018 By Jose Alberto Lorenzo
import _thread
import machine
import math
import network
import os
import time
import utime
import pycom
try:
    from machine import RTC
    from machine import SD
    from machine import Timer
    from L76GNSS import L76GNSS
    from pytrack import Pytrack
except:
    print('** No hay librerias GPS **')

import gc
gc.enable()

#Iniciar nuevo thread:  _thread.start_new_thread
# setup LoRa:
from network import LoRa
import socket
lora = LoRa(mode=LoRa.LORA)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

### Funciones

def iniciarWifi(dorsalDefault):
    try:
        import network
        from network import WLAN
        wlan = network.WLAN(mode=network.WLAN.STA)
        wlan.init(mode=WLAN.AP, ssid=dorsal, auth=(WLAN.WPA2,'witeklab@2018'), channel=1, antenna=WLAN.INT_ANT)
        from network import Server
        server = Server(login=('micro', 'python'), timeout=600)
        server.timeout(300)
        server.timeout()
        server.isrunning()
        ConfirmacionLed('wifi')
        return True
    except:
        return False

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
    funciones={'bluetooth':0x0007F,'gpsok':0xfffe02,'nogps':0x7f0000,'encendido':0x7f700,'sendalert':0xC011EB,'buscandoalerta':0xffffff}# wifi(azul) | gpsok(Amarillo) | nogps(rojo) | encendido(verde) | sendalert(lila)| -gpsok(amarillo) | buscandoalerta(blanco)
    pulsaciones(funciones[funcion])


def resetDocument():
    #Lista de documentos posible: alerta.txt | dorsal.txt | myposition.txt | registro.txt | seguidores.txt
    lista = ['alerta','dorsal','myposition','registro','seguidores','confirmacionEnlace']
    for i in lista:
        if existe(i+'.txt'):
            print('Borrando',i+'.txt')
            os.remove(i+'.txt')

def buscarMensajes(dorsal):
    alertas=[]
    while True:
        try:

            ConfirmacionLed('buscandoalerta')
            tiempo = time.time()
            s.setblocking(True)
            data = s.recv(128)
            if existe('dorsal.txt'):
                a = open('dorsal.txt')
                dorsal = a.read()
            print("Mensaje recibido:",data)
            ide =data.decode("utf-8")  #identificacion
            ide = ide.split('-')
            if ide[0] == 'alerta':
                if ide[1] not in alertas:
                    tmp = tiempo
                    alertas.append(ide[1])
                    cuenta = 0
                    for z in ide[1]:
                        if z ==";":
                            cuenta+=1
                            #print("Cuenta-->",cuenta)
                    if cuenta == 1:
                        print("Este mensaje es personalizado:",ide[1])
                        dor = ide[1].split(';')
                        if dor[0]==dorsal:
                            ConfirmacionLed('bluetooth')
                            f = open ('alertapersonalizada.txt', 'a')#Modo 'a' Para a�adir no sobre escribir
                            #print("Mensaje que se guardara = ",dor[1])
                            f.write(dor[1]+"|")
                            f.close()
                    else:
                        print("Alerta Generica",ide[0])
                        ConfirmacionLed('bluetooth')
                        f = open ('alerta.txt', 'a')#Modo 'a' Para a�adir no sobre escribir
                        f.write(ide[1]+"|")
                        f.close()
                else:
                    print("Tiempo-",tiempo,"tmp",tmp,"=",tiempo-tmp)
                    if tiempo-tmp >= 300:
                        #Si han pasado 5 minutos Borramos array alertas y ficheros del LoPy:
                        if existe('alerta.txt'):
                            os.remove('alerta.txt')
                        elif existe('alertapersonalizada.txt'):
                            os.remove('alertapersonalizada.txt')
                        del alertas[:]
                        tmp = tiempo
                print("Asi estan las alertas=",alertas)
            elif ide[0] == 'seguidores':
                dor = ide[1]
                ide = ide[1].split(';')
                print("Dorsal destino:",ide[0])
                if ide[0]==dorsal:
                    print("dentro del mismo dorsal: ",dor)
                    ConfirmacionLed('bluetooth')
                    f = open ('seguidores.txt', 'w')#Modo 'a' Para a�adir no sobre escribir
                    f.write(dor)
                    f.close()
            elif ide[0] == 'baseConfirma':
                dor = ide[1]
                ide = ide[1].split(';')
                print("Dorsal destino:",ide[0])
                if ide[0]==dorsal:
                    print("dentro del mismo dorsal: ",dor)
                    ConfirmacionLed('bluetooth')
                    f = open ('confirmacionEnlace.txt', 'w')#Modo 'a' Para a�adir no sobre escribir
                    f.write(dor)
                    f.close()
        except:
            print('** Algo ha fallado en buscarMensajes **')

def recogerPosGPSMovil():
    x = open('myposition.txt')
    x = x.read().split(';')
    lat_d = x[0]
    lon_d = x[1]
    return(lat_d, lon_d)
def buscarPos():
    try:
        py = Pytrack()
        l76 = L76GNSS(py, timeout=30)
        coord = l76.coordinates()
        return coord
    except:
        print('** Algo ha fallado en buscarPos **')
        coord = (0,0)
        return coord
def enviarPos(dorsal,dorsalDefault):
    j=0
    while True:
        if existe('myposition.txt'):
            coord = recogerPosGPSMovil()
        else:
            coord = buscarPos()
            print('Coordenadas recibidas->',coord)
            p = str(coord[0])
            if p =='None':
                coord = (0,0)
        if existe('dorsal.txt'):
            a = open('dorsal.txt')
            dorsal = a.read()
            print("Dorsal:",dorsal)
        x = "witeklab-"+str(j)+"-"+str(dorsalDefault)+"-"+str(dorsal)+"-"+str(coord[0]) + "-"+str(coord[1])
        #x = "witeklab-"+str(j)+"-"+str(dorsal)+"-"+str(coord[0]) + "-"+str(coord[1])  Antiguo!

        time.sleep(5)
        s.send(x)
        ConfirmacionLed('gpsok')
        print("Coordenadas enviadas:",x)
        j+=1
        time.sleep(30) #Pausa entre toma de coordenadas.

###     Variables
dorsal = "R2"
dorsalDefault =  dorsal

###     Main
pycom.heartbeat(False)
resetDocument()
iniciarWifi(dorsal)
print('1-> Iniciamos primer hilo Con la busqueda de mensajes:')
_thread.start_new_thread(buscarMensajes, (dorsal,))
print('2-> Iniciamos la busqueda de GPS (Fichero o localización)')
_thread.start_new_thread(enviarPos,(dorsal,dorsalDefault,))
print("-----------------------------------")
