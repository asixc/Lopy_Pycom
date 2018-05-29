import pycom
import time
def luces(color):
    for x in range(3):
        pycom.rgbled(color)
        time.sleep(0.1)
        pycom.rgbled(False)
        time.sleep(0.1)

def main():
    while True:
        print("hora:",hora)
        pycom.heartbeat(False)
        luces(0xC011EB)
        time.sleep(15)
#Crear crhono 
hora = time.time()
main(hora)
