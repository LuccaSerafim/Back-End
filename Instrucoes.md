\# Dashboard de Análise de Tráfego de Servidor



\## Setup do Backend



1\. Ativar o ambiente virtual:

.\\venv\\Scripts\\Activate.ps1





2\. Instalar dependências:

pip install -r requirements.txt





3\. Rodar o backend:

python -m uvicorn Main:app --reload --port 8080





4\. Testar no navegador:

\- Raiz: http://127.0.0.1:8080/ → mensagem de status

\- Tráfego: http://127.0.0.1:8080/traffic → dados agregados por IP



\## Observações
\- Necessário instalar Npcap no Windows para captura de pacotes.



