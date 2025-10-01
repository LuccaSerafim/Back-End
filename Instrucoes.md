\# Dashboard de Análise de Tráfego de Servidor



\## Setup do Backend



1\. Ativar o ambiente virtual:

.\\venv\\Scripts\\Activate.ps1





2\. Instalar dependências:

pip install -r requirements.txt

Se não tiver o requirements.txt, instale manualmente:

pip install flask
pip install flask-cors
pip install scapy





3\. Rodar o backend:

python Main.py





4\. Testar no navegador:

\- Raiz: http://127.0.0.1:5000 → página de status do backend

\- Tráfego: http://127.0.0.1:5000/data → retorna os dados de tráfego agregados por IP e protocolo
Observação: dependendo da rede e da máquina, o terminal do VS Code também mostrará o endereço de rede local, por exemplo http://<SEU_IP_LOCAL>:5000/data. Esse endereço (substitua <SEU_IP_LOCAL> pelo IP exibido no terminal) pode ser usado por outros dispositivos na mesma rede para acessar o backend.


\## Observações
\- Necessário instalar Npcap no Windows para captura de pacotes.



