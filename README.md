<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=blur&height=470&color=0:0044ff,50:0077ff,100:00aaff&text=ESP32%20IoT%20Pentest&textBg=false&section=header&reversal=true&fontColor=FFFFFF&fontSize=40&fontAlign=50&animation=fadeIn&desc=Segurança%20em%20IoT&descAlign=70&descSize=20" 
  alt="ESP32 IoT Pentest Banner" width="700"/>
</p>


---

<p align="center">
  Este repositório contém a análise e execução de testes de segurança (pentest) em uma aplicação IoT utilizando o ESP32. A atividade segue o roteiro proposto em aula sobre vulnerabilidades, riscos e contramedidas em IoT.
</p>

---

<p align="center">
  <img src="./assets/vid.gif" width="450" alt="Demo GIF do ESP32">
</p>


## 📂 Estrutura do Repositório

A organização deste projeto segue as entregas solicitadas na atividade ponderada:

```
PONDERADA-SEGURANCA-IOT/
 ├─ assets/              → GIFs, imagens  materiais                              
 │
 ├─ docs/                → Relatório técnico da atividade
 │   └─ documents.md     → Documento com análise, ataques e tabela de riscos
 │
 ├─ evidencias/          → Prints e provas da análise 
 │
 ├─ src/                 → Código-fonte do servidor web no ESP32 (análise estática)
 │
 └─ README.md            → Este arquivo com visão geral do projeto
```
## 👥 Integrantes do Grupo

- Anny Cerazi  
- Átila Neto  
- Eduardo Casarini  
- Giorgia Scherer  
- Leonardo Ramos  
- Lucas Faria  
- Rafael Josué  

---

## 🎯 Objetivo do Projeto

O objetivo deste projeto é analisar a segurança de um sistema IoT baseado no ESP32 que hospeda um servidor web local capaz de controlar remotamente GPIOs (pinos 26 e 27) através de comandos HTTP.

Esse sistema possibilita o acionamento de dispositivos (como LEDs ou relés) usando uma página web, permitindo que qualquer dispositivo conectado à mesma rede Wi-Fi consiga ligar ou desligar os pinos.

A partir dessa implementação, o projeto visa:


✔ Avaliar riscos associados ao controle remoto de hardware via rede Wi-Fi
✔ Testar exploração de falhas como injeção de comandos e spoofing de acesso
✔ Apresentar melhorias para aumentar a proteção contra ataques reais

# Ataques: 
Durante a análise do servidor web rodando no ESP32, foram exploradas diversas vulnerabilidades de segurança que permitiram a realização de ataques bem-sucedidos. Entre eles, destacam-se: tentativa de adivinhação e exploração de falhas de autenticação, múltiplas requisições simultâneas para estressar o sistema (DoS simplificado), varredura de endpoints expostos e interceptação/observação de respostas para identificar comportamentos inseguros. A partir desses testes, foi possível demonstrar que a aplicação não implementa controle de acesso robusto nem mecanismos de mitigação, permitindo que um invasor tenha acesso ao sistema mesmo sem credenciais válidas.