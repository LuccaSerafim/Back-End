# -*- coding: utf-8 -*-

"""
Backend Aprimorado para o Dashboard de Análise de Tráfego de Servidor.

Esta versão combina o melhor de duas abordagens:
1. Detecção automática do IP e da interface de rede do servidor.
2. Captura de pacotes mais eficiente usando filtros BPF.
3. Lógica robusta de agregação em janelas de tempo fixas.
4. Estrutura de dados completa para suportar o drill down por protocolo.
"""

import time
import threading
import socket
from collections import defaultdict
from flask import Flask, jsonify
from flask_cors import CORS
from scapy.all import sniff, IP, TCP, UDP, ICMP, get_if_list, get_if_addr

# --- CONFIGURAÇÃO AUTOMÁTICA ---

def get_main_ip_and_iface():
    """
    Detecta o IP privado principal e a interface de rede correspondente.
    Funciona criando uma conexão UDP temporária para um IP público.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # Não precisa enviar dados, só conectar
        s.connect(('8.8.8.8', 80))
        server_ip = s.getsockname()[0]
    except Exception:
        # Fallback se não houver conexão com a internet
        server_ip = '127.0.0.1'
    finally:
        s.close()
    
    server_iface = None
    for iface in get_if_list():
        try:
            if get_if_addr(iface) == server_ip:
                server_iface = iface
                break
        except Exception:
            continue
            
    if not server_iface:
        print("AVISO: Não foi possível detectar a interface de rede automaticamente. Usando a interface padrão.")

    return server_ip, server_iface

SERVER_IP, SERVER_IFACE = get_main_ip_and_iface()
TIME_WINDOW = 5  # Segundos

print("-" * 50)
print(f"IP do servidor detectado automaticamente: {SERVER_IP}")
print(f"Escutando na interface: {SERVER_IFACE or 'Padrão'}")
print("-" * 50)


# Estrutura para armazenar os dados de tráfego (preparada para drill down)
traffic_data = defaultdict(lambda: {
    "inbound": 0,
    "outbound": 0,
    "protocols": defaultdict(lambda: {"inbound": 0, "outbound": 0})
})

# Lock para garantir acesso thread-safe à estrutura de dados
data_lock = threading.Lock()

def process_packet(packet):
    """
    Função de callback para cada pacote capturado.
    Processa e agrega os dados de tráfego.
    """
    # A verificação 'if IP in packet' já é implicitamente tratada pelo filtro BPF,
    # mas mantemos por segurança.
    if not packet.haslayer(IP):
        return

    try:
        packet_ip = packet[IP]
        packet_size = len(packet)
        protocol_name = "OUTROS"

        if packet.haslayer(TCP):
            protocol_name = "TCP"
        elif packet.haslayer(UDP):
            protocol_name = "UDP"
        elif packet.haslayer(ICMP):
            protocol_name = "ICMP"
        
        client_ip = None
        direction = None

        if packet_ip.src == SERVER_IP:
            direction = "outbound"
            client_ip = packet_ip.dst
        elif packet_ip.dst == SERVER_IP:
            direction = "inbound"
            client_ip = packet_ip.src
        
        # Este 'else' não deveria acontecer devido ao filtro "host", mas é uma boa prática
        else:
            return

        with data_lock:
            # Atualiza o total de bytes para o cliente
            traffic_data[client_ip][direction] += packet_size
            # Atualiza o total de bytes para o protocolo (para o drill down)
            traffic_data[client_ip]["protocols"][protocol_name][direction] += packet_size

    except Exception as e:
        print(f"Erro ao processar pacote: {e}")


def reset_data_loop():
    """
    Thread que zera os dados de tráfego a cada janela de tempo.
    Isto garante uma janela de tempo consistente e fixa.
    """
    global traffic_data
    while True:
        time.sleep(TIME_WINDOW)
        with data_lock:
            traffic_data.clear()
        # print(f"Dados zerados. Nova janela de {TIME_WINDOW}s iniciada.")


# --- Configuração da API Flask ---
app = Flask(__name__)
CORS(app)

@app.route('/data')
def get_traffic_data():
    """Endpoint da API que retorna os dados de tráfego atuais."""
    with data_lock:
        return jsonify(dict(traffic_data))


if __name__ == '__main__':
    print("Iniciando o monitoramento de tráfego...")
    
    reset_thread = threading.Thread(target=reset_data_loop, daemon=True)
    reset_thread.start()
    
    # Inicia a thread de captura com o filtro BPF eficiente e a interface detectada
    capture_thread = threading.Thread(
        target=lambda: sniff(
            prn=process_packet,
            filter=f"host {SERVER_IP}", # Filtro BPF, muito mais eficiente
            store=False,
            iface=SERVER_IFACE # Especifica a interface a ser escutada
        ),
        daemon=True
    )
    capture_thread.start()
    
    print(f"Dashboard API rodando em http://127.0.0.1:5000")
    
    app.run(host="0.0.0.0", port=5000, debug=False)
