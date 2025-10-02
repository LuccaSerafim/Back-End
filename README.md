# 🚀 Backend - Dashboard de Análise de Tráfego de Servidor  
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)  
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green?logo=fastapi)  
![License](https://img.shields.io/badge/license-MIT-black)

Backend desenvolvido em **FastAPI** para monitoramento e análise de tráfego de rede em tempo real. Ele captura pacotes da interface de rede e expõe endpoints REST para consumo pelo frontend.

---

## 📂 Estrutura do Projeto

Back-End/  
Esqueleto-Inicial/  
└── main.py                # Código base inicial do backend  
Esqueleto-Completo/  
└── main.py                # Versão completa do backend  
Teste-Requestes/          # Testes HTTP para o backend  
└── *.http                 # Arquivos de teste .http para REST Client  
requirements.txt          # Dependências do projeto  
README.md                 # Documentação do projeto  
Instrucoes.md             # Instruções adicionais  

---

## ⚙️ Instalação e Execução

### 1. Clone o repositório  
  
git clone https://github.com/Trabalho-Redes/Back-End.git |
cd Back-End



### 2. Crie e ative o ambiente virtual  
python -m venv venv |
.\venv\Scripts\Activate.ps1


### 3. Instale as dependências  
pip install -r requirements.txt


### 4. Execute o backend  
python main.py


### 5. Acesse no navegador  
- [http://127.0.0.1:5000](http://127.0.0.1:5000) → status do backend  
- [http://127.0.0.1:5000/data](http://127.0.0.1:5000/data) → dados de tráfego  

💡 O terminal também exibirá um endereço na rede local (ex: http://192.168.x.x:5000/data), que pode ser usado por outros dispositivos conectados à mesma rede.

---

## 📡 Endpoints

- **GET /**  
  Retorna status do backend.  
{"status": "Backend de análise de tráfego ativo."}


- **GET /data**  
Retorna tráfego agregado por IP e protocolo.  
{
"192.168.0.10": {
"inbound": {"TCP": 12, "UDP": 4},
"outbound": {"TCP": 8}
}
}


---

## 🧪 Testes Rápidos  

O repositório inclui `Teste-Requestes/` com arquivos `.http` para uso com a extensão REST Client no VS Code:

- **Testando status do backend**  
GET http://127.0.0.1:5000/

- **Testando tráfego local**  
GET http://127.0.0.1:5000/data

- **Testando acesso via rede local**  
GET http://<SEU_IP_LOCAL>:5000/data

---

## ⚠️ Observações Importantes

- É necessário instalar **Npcap** (Windows) para captura de pacotes.  
- O backend captura dados apenas da interface de rede principal.  
- Os dados são agregados em janelas de tempo de 5s. Caso não haja tráfego recente, o endpoint `/data` pode retornar vazio.  
- Para testar manualmente, gere tráfego com:
- ping 127.0.0.1 |
curl http://127.0.0.1:5000/data
