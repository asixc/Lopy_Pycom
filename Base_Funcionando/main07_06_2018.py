#Generado el 07-06-2018
from network import LoRa
from machine import Timer
import socket
import machine
import time
import os
import pycom
import _thread
import gc

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

def ConfirmacionLed(funcion):
    funciones={'wifi':0x0007F,'recibido':0xfffe02,'nogps':0x7f0000,'encendido':0x7f700,'sendalert':0xC011EB}# wifi(azul) | recibido(Amarillo) | nogps(rojo) | encendido(verde) | sendalert(lila) -gpsok()
    pulsaciones(funciones[funcion])

def enviarAlertas(s,listalertas=[]):
    a = open('alertas.txt')
    j = a.read()
    j = j.strip("|")
    j = j.split("|")
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
    print('2-> Iniciamos seguno hilo con la busqueda de alertas:')
    while True:
        try:
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
        except:
            print("*** - Algo ha fallado en IniciarAlertas - ***")

def iniciarSeguidores(lora,s,tiempoEnvioSeguidores):
    s.setblocking(False)
    tiempo = time.time()
    tmp=tiempo
    print('3-> Iniciamos el tercer hilo con la busqueda de seguidores')
    while True:
        try:
            time.sleep(12)
            tiempo=time.time()
            if existe('seguidores.txt'):
                if tiempo-tmp >= tiempoEnvioSeguidores:
                    tmp=tiempo
                    a = open('seguidores.txt')
                    j = a.read()
                    j = j.replace('\r','')
                    j = j.replace('\n','')
                    j = j.strip("|")
                    j = j.split("|")
                    b= len(j)
                    print("N seguidores",b)
                    for x in range(b):
                        msg = "seguidores-"+j[x]
                        s.send(msg)
                        print("Mensaje enviado:",msg)
                        ConfirmacionLed('sendalert')
                else:
                    print("Seguidores.txt existe pero Aun no han pasado X segundos",tiempo-tmp)
            else:
                print("- No hay Seguidores(Archivo 'seguidores.txt' no existe.)")
        except:
            print('*** - Algo ha fallado en IniciarSeguidores - ***')

def iniciarCorredores(lora,s,tiempoVaciarBasura):
    print('1-> Iniciamos primer hilo el registro de corredores:')
    corredores=[]
    while True:
        try:
            actualizado = 0
            s.setblocking(True)
            data = s.recv(64) #socket.recv (bufsize [, flags])  Reciba datos del socket. El valor de retorno es una cadena que representa los datos recibidos. La cantidad máxima de datos que se recibirán a la vez se especifica mediante bufsize
            j =data.decode("utf-8")
            j = j.split('-')
            if j[0] == 'witeklab':
                #j[dorsalDefault],j[dorsalactual],j[contador],j[latitud],j[Longitud]
                print('mensaje entrante->',data)
                for c in range(len(corredores)):
                    if j[2] in corredores[c]:
                        if int(j[1]) > int(corredores[c][2]):
                            corredores[c]=([j[2],j[3],j[1],j[4],j[5]])
                            ConfirmacionLed('recibido')
                            actualizado=1
                            break
                if actualizado==0:
                    corredores.append([j[2],j[3],j[1],j[4],j[5]])
                    msj = "baseConfirma-"+j[2]+";OK"
                    s.send(msj)
                    ConfirmacionLed('recibido')

            print("Corredores:",len(corredores))
            print(corredores)
            print("Memoria libre actual->",gc.mem_free())
            #print(gc.isenabled())
            #print("crono->",crono.read())
            if crono.read() > tiempoVaciarBasura :
                gc.collect()
                crono.reset()
                print("Vaciando papelera...Memoria disponible:",gc.mem_free())

            #linea = j[2]+";"+j[1]+";"+j[3]";"+j[4]+"|" #ID;NºRegistro;Latitud;Longitud|
            f = open ('registro.txt', 'w')#Modo 'a' Para añadir no sobre escribir
            for c in range(len(corredores)):
                if len(corredores)!=0:
                    d = corredores[c]
                    texto = d[1]+";"+d[3]+";"+d[4]+"|"
                    f.write(texto)
            f.close()
        except Exception as e:
            print("*** - Algo ha fallado en IniciarCorredores - *** -> ",e)

def escucharBaseRepetidora():
    port = 12345
    print('4-> Iniciamos el cuarto hilo con la espera de recibir el registro de la base repetidora')
    while True:
        try:

            while True:
                s = socket.socket()
                s.bind(socket.getaddrinfo("0.0.0.0", port)[0][4])
                s.listen(2s)
                print("Mostramos listado:",os.listdir())
                if existe('registro2.txt'):
                    print("Mostramos contenido fichero registro2.txt:")
                    print(open('registro2.txt').read())
                    pass

                print("\n\nEsperando conexion")
                readable, writable, errored = select.select([s], [], [])
                for s in readable:
                    cl, remote_addr = s.accept()
                    cl.setblocking(True)
                    cl.settimeout(2)
                    print("Client connection from:", remote_addr)
                    file = "/flash/registro2.txt"
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
                print("Recibido...Faltaría actualizar corredores")
                s.close()
        except:
            print("*** - Algo ha fallado en escucharBaseRepetidora - ***")


###     Variables
pssid = "Gateway1"
tiempoEnvioSeguidores = 20
tiempoVaciarBasura = 100
lora = LoRa(mode=LoRa.LORA)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
crono = Timer.Chrono()
crono.start()
###     Main
pycom.heartbeat(False)
resetDocument()
iniciarWifi(pssid)
time.sleep(0.2)
a = _thread.start_new_thread(iniciarCorredores,(lora,s,tiempoVaciarBasura,))
time.sleep(0.3)
b = _thread.start_new_thread(inciarAlertas,(lora,s,))
time.sleep(0.2)
c = _thread.start_new_thread(iniciarSeguidores,(lora,s,tiempoEnvioSeguidores,))
time.sleep(0.3)
#Pendiente implantacion:
_thread.start_new_thread(escucharBaseRepetidora,())
time.sleep(0.2)
