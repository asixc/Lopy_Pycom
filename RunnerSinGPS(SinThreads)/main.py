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

# setup LoRa:
from network import LoRa
import socket
lora = LoRa(mode=LoRa.LORA)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# setup as a station
import gc
time.sleep(2)
gc.enable()

def iniciarFTP():
    try:
        import network
        from network import WLAN
        wlan = network.WLAN(mode=network.WLAN.STA)
        wlan.init(mode=WLAN.AP, ssid='Runner3NoGPS', auth=(WLAN.WPA2,'witeklab@2018'), channel=1, antenna=WLAN.INT_ANT)
        from network import Server
        server = Server(login=('micro', 'python'), timeout=600)
        server.timeout(300)
        server.timeout()
        server.isrunning()
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
#    pycom.rgbled(0x0007F)#azul               wifion
#    pycom.rgbled(0xC011EB)#Lila             enviando alerta
#    pycom.rgbled(0xfffe02)#Amarillo          gps ok
#    pycom.rgbled(0x7f0000)#Rojo suave       gps off
#    pycom.rgbled(0x7f700)#verde             encendido
#    pycom.rgbled(0xfb0c86) #rosa
#    pycom.rgbled(0xffffff) #blanco         Buscando alerta

def ConfirmacionLed(funcion):
    funciones={'bluetooth':0x0007F,'gpsok':0xfffe02,'nogps':0x7f0000,'encendido':0x7f700,'sendalert':0xC011EB,'buscandoalerta':0xffffff}# wifi(azul) | gpsok(Amarillo) | nogps(rojo) | encendido(verde) | sendalert(lila)| -gpsok(amarillo) | buscandoalerta(blanco)
    pulsaciones(funciones[funcion])

def buscarMensajes(alertas,dorsal,tiempo,tmp):
    ConfirmacionLed('buscandoalerta')
    for x in range(10):
        s.setblocking(False)
        data = s.recv(128)
        print("Mensaje recibido:",data)
        ide =data.decode("utf-8")  #identificacion
        ide = ide.split('-')
        if ide[0] == 'alerta':
            ConfirmacionLed('sendalert')
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
        time.sleep(3)
    return alertas,tmp

def recogerPosGPSMovil():
    x = open('myposition.txt')
    x = x.read().split(';')
    lat_d = x[0]
    lon_d = x[1]
    return(lat_d, lon_d)

def resetDocument():
    #Lista de documentos posible: alerta.txt | dorsal.txt | myposition.txt | registro.txt | seguidores.txt
    lista = ['alerta','dorsal','myposition','registro','seguidores']
    for i in lista:
        if existe(i+'.txt'):
            print('Borrando',i+'.txt')
            os.remove(i+'.txt')

# setup rtc
rtc = machine.RTC()
rtc.ntp_sync("0.pool.ntp.org")
chrono = Timer.Chrono()
chrono.start()

#Bucle de led's Indicando inicio de ejecuci�n:
pycom.heartbeat(False)
ConfirmacionLed('encendido')
iniciarFTP()                 #Iniciar wifi en modo servidor personalizado SSID
pycom.heartbeat(False)       #Apagado del led al comenzar
resetDocument()              #Borrado inicial
#Variables:
dorsalDefault="Runner3NoGPS"
dorsal = dorsalDefault
j=0
alertas=[]
leido = 0
tmp = time.time()
tmp2=0
timeborrado=0

while (True):
    s.setblocking(True)
    tiempo = time.time()
    #Control tiempo del fichero myposition.txt
    if existe('myposition.txt'):
        if tmp2!=0:
            tmp3 = os.stat('myposition.txt')    #obtenemos datos del archivo
            fmodi2 = tmp3[8]
            if fmodi2-fmodi==0: #Si la diferencia entre archivos es la misma quiere decir que es el mismo
                if timeborrado==0:
                    timeborrado=time.time()
                else:
                    print("Dentro del else del tiempo obtenido y sigue sin modificarse")
                    print("Miramos el tiempo:",time.time()-timeborrado)
                    if time.time()-timeborrado >= 60*9: #60 segundos por 9 = 9 minutos.
                        print("El tiempo es superior a 2 minutos ...borramos dorsal,txt")
                        #borramos archivo
                        os.remove('myposition.txt')
                        tmp2=0
                        timeborrado=0
            else:
                tmp2=0
                timeborrado=0
        else:
            tmp2 = os.stat('myposition.txt')    #obtenemos datos del archivo
            fmodi = tmp2[8]

    #Recoger posición gps del móvil si existe el fichero:
    if existe('myposition.txt'):
        coord = recogerPosGPSMovil()
    else:
        coord = (0,0)

    #Enviar la posición con el dorsal si existe el fichero o el default:
    if existe('dorsal.txt'):
        a = open('dorsal.txt')
        dorsal = a.read()
        print("Dorsal:",dorsal)
        x = "witeklab-"+str(j)+"-"+str(dorsal)+"-"+str(coord[0]) + "-"+str(coord[1])
    else:
        x = "witeklab-"+str(j)+"-"+dorsalDefault+"-"+str(coord[0]) + "-"+str(coord[1])

    p = str(coord[0])
    if p =='None':
        ConfirmacionLed('nogps')
        print("Buscando -",nintentos)
        nintentos+=1
    else:
        s.send(x)
        ConfirmacionLed('gpsok')
        print("Coordenadas enviadas:",x)
        j+=1
        time.sleep(30) #Pausa entre toma de coordenadas.

    #En caso de existir dorsal, se buscará alerta.
    ConfirmacionLed('buscandoalerta')

    alertas,tmp =buscarMensajes(alertas,dorsal,tiempo,tmp)
