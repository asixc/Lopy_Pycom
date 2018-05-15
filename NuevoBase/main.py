#Generado el 10-09-2018
from network import LoRa
import socket
import machine
import time
import os
import pycom
import _thread

###     Funciones
def existe(arg):
    try:
        fichero = open(arg)
        fichero.close()
        return True
    except:
        return False

def iniciarWifi(pssid):
    try:
        import network
        from network import WLAN
        wlan = network.WLAN(mode=network.WLAN.STA)
        wlan.init(mode=WLAN.AP, ssid=pssid, auth=(WLAN.WPA2,'witeklab@2018'), channel=7, antenna=WLAN.INT_ANT)
        from network import Server
        server = Server(login=('micro', 'python'), timeout=600)
        server.timeout(300)
        server.timeout()
        server.isrunning()
        ConfirmacionLed('wifi')
        return True
    except:
        return False

def resetDocument():
    #Lista de documentos posible: alerta.txt | dorsal.txt | myposition.txt | registro.txt | seguidores.txt
    lista = ['alertas','dorsal','myposition','registro','seguidores','alertapersonalizada']
    for i in lista:
        if existe(i+'.txt'):
            print('Borrando',i+'.txt')
            os.remove(i+'.txt')

def pulsaciones(color):
    for x in range(3):
        pycom.rgbled(color)
        time.sleep(0.1)
        pycom.heartbeat(False)
        time.sleep(0.2)
#    pycom.rgbled(0x0007F)#azul               wifion
#    pycom.rgbled(0xC011EB)#Lila             enviando alerta
#    pycom.rgbled(0xfffe02)#Amarillo          gps ok
#    pycom.rgbled(0x7f0000)#Rojo suave       gps off
#    pycom.rgbled(0x7f700)#verde             encendido
#    pycom.rgbled(0xfb0c86) #rosa

def ConfirmacionLed(funcion):
    funciones={'wifi':0x0007F,'recibido':0xfffe02,'nogps':0x7f0000,'encendido':0x7f700,'sendalert':0xC011EB}# wifi(azul) | recibido(Amarillo) | nogps(rojo) | encendido(verde) | sendalert(lila) -gpsok()
    pulsaciones(funciones[funcion])

def enviarAlertas(s,listalertas=[]):
    a = open('alertas.txt')
    j = a.read()
    j = j.strip('|')
    j = j.split('|')
    b= len(j)
    print("N alertas=",b)
    for x in range(b):
        j[x] = j[x].replace('\n','')
        j[x] = j[x].replace('\r','')
        if j[x] not in listalertas:
            listalertas.append(j[x])
            cuenta = 0
            for z in j[x]:
                if z =="-":
                    cuenta+=1
            print("Cuenta-->",cuenta)
            if cuenta == 1:
                print("Mensaje Personalizado no estaba guardado:",j[x])
                p=j[x].split("-")
                msg = "alerta-"+p[1].replace(' ','')+";"+p[0]
                s.send(msg)
            else:
                j[x]
                print("Mensaje no estaba guardado:",j[x])
                msg = "alerta-"+j[x]
                s.send(msg)
            #Mostramos para comprobar el mensaje enviado:
            print("Mensaje enviado:",msg)
            ConfirmacionLed('sendalert')
            print("Asi esta la lista: ",listalertas)
    return listalertas

def inciarAlertas(lora,s):
    listalertas=[]
    s.setblocking(False)
    tiempo=time.time()
    tmp2=tiempo
    re=0
    while True:
        time.sleep(30)
        tiempo=time.time()
        if existe('alertas.txt'):
            if re==0:
                listalertas = enviarAlertas(s,listalertas)
                tmp2=tiempo
                re+=1
            elif tiempo-tmp2>=60 and re !=0:
                tmp2=tiempo
                print("Reenviando la lista de alertas")
                del listalertas[:] #Borro la lista y reenvio leyendo de nuevo.
                listalertas = enviarAlertas(s,listalertas)
            else:
                print("Alertas existe, pero aun no ha pasado los 60 segundos=", tiempo-tmp2)
        else:
            print("- No hay alertas(Archivo 'alertas.txt' no existe.)")
            del listalertas[:]
            re=0

def iniciarSeguidores(lora,s):
    s.setblocking(False)
    tiempo = time.time()
    tmp=tiempo
    while True:
        time.sleep(24)
        tiempo=time.time()
        if existe('seguidores.txt'):
            if tiempo-tmp >= 120 :
                tmp=tiempo
                a = open('seguidores.txt')
                j = a.read()
                j = j.split('|')
                b= len(j)
                print("N seguidores",b)
                for x in range(b):
                    j[x] = j[x].replace('\n','')
                    j[x] = j[x].replace('\r','')
                    msg = "seguidores-"+j[x]
                    s.send(msg)
                    print("Mensaje enviado:",msg)
                    ConfirmacionLed('sendalert')
            else:
                print("Seguidores.txt existe pero Aun no han pasado 120 segundos",tiempo-tmp)
        else:
            print("- No hay Seguidores(Archivo 'seguidores.txt' no existe.)")

def iniciarCorredores(lora,s):
    corredores=[]
    while True:
        actualizado = 0
        s.setblocking(True)
        data = s.recv(64) #socket.recv (bufsize [, flags])  Reciba datos del socket. El valor de retorno es una cadena que representa los datos recibidos. La cantidad máxima de datos que se recibirán a la vez se especifica mediante bufsize
        j =data.decode("utf-8")
        j = j.split('-')
        if j[0] == 'witeklab':
            print('mensaje entrante->',data)
            for c in range(len(corredores)):
                if j[2] in corredores[c]:
                    corredores[c]=([j[2],j[3],j[4],j[5]])
                    ConfirmacionLed('recibido')
                    actualizado=1
                    break
            if actualizado==0:
                corredores.append([j[2],j[3],j[4],j[5]])
                ConfirmacionLed('recibido')

        print("Corredores:",len(corredores))
        print(corredores)

        #linea = j[2]+";"+j[1]+";"+j[3]";"+j[4]+"|" #ID;NºRegistro;Latitud;Longitud|
        f = open ('registro.txt', 'w')#Modo 'a' Para añadir no sobre escribir
        for c in range(len(corredores)):
            if len(corredores)!=0:
                d = corredores[c]
                texto = d[1]+";"+d[2]+";"+d[3]+"|"
                f.write(texto)
        f.close()

###     Variables
pssid = "Gateway1"
lora = LoRa(mode=LoRa.LORA)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
###     Main
pycom.heartbeat(False)
resetDocument()
iniciarWifi(pssid)
print('1-> Iniciamos primer hilo el registro de corredores:')
a = _thread.start_new_thread(iniciarCorredores,(lora,s,))
print('2-> Iniciamos seguno hilo con la busqueda de alertas:')
b = _thread.start_new_thread(inciarAlertas,(lora,s,))
print('3-> Iniciamos el tercer hilo con la busqueda de seguidores')
c = _thread.start_new_thread(iniciarSeguidores,(lora,s))
