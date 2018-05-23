import _thread
import machine
import math
import network
import os
import time
import utime
import pycom
def finalizar(u,d):
    time.sleep()
def main():
    pycom.heartbeat(False)
    resetDocument()
    iniciarWifi(dorsal)
    print('1-> Iniciamos primer hilo Con la busqueda de mensajes:')
    uno = _thread.start_new_thread(buscarMensajes, (dorsal,))
    print('2-> Iniciamos la busqueda de GPS (Fichero o localización)')
    dos = _thread.start_new_thread(enviarPos,(dorsal,dorsalDefault,))
    finalizar(uno,dos)
    print("-----")
