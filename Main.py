from fastapi import FastAPI
from scapy.all import sniff, IP
from threading import Thread, Lock
import time

app = FastAPI()

# -----------------------------
# Endpoint raiz
# -----------------------------
@app.get("/")
def read_root():
    return {"message": "Backend rodando e pronto para capturar tráfego 🚀"}

# -----------------------------
# Variáveis globais
# -----------------------------
SERVER_IP = " 192.168.0.1"  # Substitua pelo seu IP
window_time = 5  # segundos
traffic_data = {}  # {"ip_cliente": {"incoming": int, "outgoing": int}}
lock = Lock()

# -----------------------------
# Função de captura de pacotes
# -----------------------------
def packet_handler(packet):
    if IP in packet:
        src = packet[IP].src
        dst = packet[IP].dst
        length = len(packet)
        
        with lock:
            if src == SERVER_IP:
                if dst not in traffic_data:
                    traffic_data[dst] = {"incoming": 0, "outgoing": 0}
                traffic_data[dst]["outgoing"] += length
            elif dst == SERVER_IP:
                if src not in traffic_data:
                    traffic_data[src] = {"incoming": 0, "outgoing": 0}
                traffic_data[src]["incoming"] += length

def capture_loop():
    sniff(prn=packet_handler, filter=f"host {SERVER_IP}", store=False)

# Rodar captura em thread separada
t = Thread(target=capture_loop, daemon=True)
t.start()

# -----------------------------
# Endpoint de tráfego
# -----------------------------
@app.get("/traffic")
def get_traffic():
    with lock:
        data_snapshot = dict(traffic_data)
        traffic_data.clear()
    return data_snapshot

