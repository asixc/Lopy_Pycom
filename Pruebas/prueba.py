import pycom
import time
def luces(color):
    for x in range(3):
        pycom.rgbled(color)
        time.sleep(0.1)
        pycom.rgbled(False)
        time.sleep(0.1)

def main():
    luces(0xC011EB)

main()
