from fastapi import FastAPI
from scapy.all import sniff, IP, get_if_list, get_if_addr
from threading import Thread, Lock
import socket

app = FastAPI()

# -----------------------------
# Endpoint raiz
# -----------------------------
@app.get("/")
def read_root():
    return {"message": "Backend rodando e pronto para capturar tráfego 🚀"}

# -----------------------------
# Detectando interface e IP principal automaticamente
# -----------------------------
def get_private_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Conecta a um IP público arbitrário
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

SERVER_IP = get_private_ip()

# Descobre a interface correspondente ao IP detectado
SERVER_IFACE = None
for iface in get_if_list():
    try:
        if get_if_addr(iface) == SERVER_IP:
            SERVER_IFACE = iface
            break
    except Exception:
        continue

window_time = 20  # segundos para reset do tráfego
traffic_data = {}  # {"ip_cliente": {"incoming_bytes": int, "outgoing_bytes": int, "total_bytes": int}}
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
                    traffic_data[dst] = {"incoming_bytes": 0, "outgoing_bytes": 0, "total_bytes": 0}
                traffic_data[dst]["outgoing_bytes"] += length
            elif dst == SERVER_IP:
                if src not in traffic_data:
                    traffic_data[src] = {"incoming_bytes": 0, "outgoing_bytes": 0, "total_bytes": 0}
                traffic_data[src]["incoming_bytes"] += length

            # Atualiza total
            if src == SERVER_IP or dst == SERVER_IP:
                ip = dst if src == SERVER_IP else src
                traffic_data[ip]["total_bytes"] = traffic_data[ip]["incoming_bytes"] + traffic_data[ip]["outgoing_bytes"]

# -----------------------------
# Loop de captura
# -----------------------------
def capture_loop():
    sniff(prn=packet_handler, filter=f"host {SERVER_IP}", store=False, iface=SERVER_IFACE)

# Rodar captura em thread separada
t = Thread(target=capture_loop, daemon=True)
t.start()

# -----------------------------
# Endpoint de tráfego
# -----------------------------
@app.get("/traffic")
def get_traffic():
    with lock:
        if not traffic_data:
            return {"message": "Nenhum tráfego registrado ainda."}
        data_snapshot = dict(traffic_data)
        traffic_data.clear()
    return data_snapshot
