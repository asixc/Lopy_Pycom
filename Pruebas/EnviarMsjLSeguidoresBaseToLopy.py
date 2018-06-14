
import socket
from network import LoRa

lora = LoRa(mode=LoRa.LORA, frequency=868000000, tx_power=14, bandwidth=LoRa.BW_125KHZ, sf=7)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
msg = "seguidores-777;6;977;41.55666866;2.0252169;11:32:55"
s.send(msg)
print("Mensaje enviado:",msg)
