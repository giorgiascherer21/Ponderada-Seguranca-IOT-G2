# Relatório Técnico de Análise de Segurança: Servidor Web ESP32

## 1. Introdução

Este relatório técnico apresenta os resultados da análise de segurança estática realizada sobre o código-fonte de um servidor web simples implementado em um microcontrolador ESP32, utilizando a IDE do Arduino. O objetivo é identificar vulnerabilidades (pontos fracos), descrever possíveis ataques e quantificar o risco associado a cada um, conforme solicitado.

O código analisado permite o controle de dois pinos GPIO (26 e 27) através de uma interface web acessível via rede local.

## 2. Análise Estática do Código e Vulnerabilidades

A análise estática do código-fonte (`esp32_webserver_code.ino`) revelou duas vulnerabilidades principais (pontos fracos) decorrentes de práticas de programação inseguras, comuns em ambientes de prototipagem e tutoriais.

### 2.1. Vulnerabilidade 1: Falta de Autenticação e Autorização (CWE-287)

O servidor web processa comandos de controle de GPIOs diretamente com base na URL da requisição HTTP, sem qualquer verificação de identidade ou permissão do cliente.

**Evidência no Código:**
A lógica de controle dentro da função `loop()` é executada imediatamente após a recepção do cabeçalho HTTP:

```cpp
// turns the GPIOs on and off
if (header.indexOf("GET /26/on") >= 0) {
  Serial.println("GPIO 26 on");
  output26State = "on";
  digitalWrite(output26, HIGH);
} else if (header.indexOf("GET /26/off") >= 0) {
// ... e assim por diante para os outros comandos
```

**Ponto Fraco:** Qualquer dispositivo conectado à mesma rede Wi-Fi que conheça o endereço IP do ESP32 pode enviar comandos para ligar ou desligar os GPIOs, comprometendo a integridade do sistema controlado.

### 2.2. Vulnerabilidade 2: Falha na Limitação de Buffer de Entrada (CWE-119 / CWE-789)

O código utiliza um objeto `String` (`String header;`) para armazenar o cabeçalho HTTP completo recebido do cliente. Não há mecanismos de validação ou limitação de tamanho para esta *string* antes de seu processamento.

**Evidência no Código:**
A leitura de cada caractere do cliente é concatenada diretamente à variável `header`:

```cpp
char c = client.read();             // read a byte, then
// ...
header += c;
```

**Ponto Fraco:** A classe `String` do Arduino utiliza alocação dinâmica de memória (heap). Se um atacante enviar um cabeçalho HTTP excessivamente longo, a alocação contínua de memória pode esgotar o *heap* disponível do ESP32, levando a uma falha de alocação e, consequentemente, a um *crash* do sistema ou a um comportamento instável.

## 3. Análise de Ataques

Com base nas vulnerabilidades identificadas, descrevemos dois ataques potenciais, detalhando o passo-a-passo, probabilidade, impacto e risco.

### 3.1. Ataque 1: Consumo de Memória (Denial of Service - DoS)

Este ataque explora a **Vulnerabilidade 2 (Falha na Limitação de Buffer)** para causar uma negação de serviço (DoS) por exaustão de recursos de memória.

#### Passo-a-Passo do Ataque:

1.  **Identificação do Alvo:** O atacante descobre o endereço IP do ESP32 na rede local (ex: `192.168.1.100`).
2.  **Criação da Requisição Maliciosa:** O atacante utiliza uma ferramenta (ex: `netcat`, `curl` ou um script Python) para enviar uma requisição HTTP com um cabeçalho extremamente longo. O cabeçalho pode ser composto por um campo HTTP não padrão repetido milhares de vezes.
    *   *Exemplo de Requisição:*
        ```
        GET / HTTP/1.1
        Host: 192.168.1.100
        X-Long-Header: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA... (milhares de 'A')
        \r\n\r\n
        ```
3.  **Execução:** O ESP32 recebe a requisição. A linha `header += c;` tenta alocar e concatenar a *string* gigantesca na memória *heap*.
4.  **Resultado:** O ESP32 esgota sua memória RAM disponível, a alocação falha, e o dispositivo entra em um estado de falha (possivelmente um *reboot* ou *crash*), tornando o servidor web indisponível.

#### Avaliação de Risco:

| Métrica | Valor | Justificativa |
| :--- | :--- | :--- |
| **Probabilidade** | **Alta (3)** | A execução é trivial e não requer conhecimento avançado. Qualquer cliente na rede pode enviar uma requisição longa. A vulnerabilidade é uma falha de design fundamental no tratamento de entrada. |
| **Impacto** | **Alto (3)** | O resultado é a indisponibilidade total do servidor web e, potencialmente, o *crash* do microcontrolador, exigindo um *reboot* manual ou automático para recuperação. Isso interrompe todas as funcionalidades do dispositivo. |
| **Risco** | **Crítico (9)** | A combinação de alta probabilidade e alto impacto resulta em um risco crítico, pois a falha pode ser explorada facilmente para desativar o dispositivo. |

### 3.2. Ataque 2: Controle Não Autorizado de GPIOs

Este ataque explora a **Vulnerabilidade 1 (Falta de Autenticação)** para manipular os dispositivos conectados ao ESP32 (LEDs, relés, etc.) sem permissão.

#### Passo-a-Passo do Ataque:

1.  **Identificação do Alvo:** O atacante descobre o endereço IP do ESP32 na rede local (ex: `192.168.1.100`).
2.  **Descoberta de Comandos:** O atacante infere ou observa os comandos de controle de GPIOs (ex: `/26/on`, `/27/off`).
3.  **Execução:** O atacante envia uma requisição HTTP simples para o ESP32 com o comando desejado.
    *   *Exemplo de Requisição (via navegador ou `curl`):*
        ```
        http://192.168.1.100/26/on
        ```
4.  **Resultado:** O ESP32 executa o comando `digitalWrite(output26, HIGH);`, ligando o dispositivo conectado ao GPIO 26, sem que o usuário legítimo seja notificado ou tenha dado permissão.

#### Avaliação de Risco:

| Métrica | Valor | Justificativa |
| :--- | :--- | :--- |
| **Probabilidade** | **Média (2)** | A vulnerabilidade é óbvia, mas o ataque requer que o atacante esteja na mesma rede local (limitação de escopo). A simplicidade do comando aumenta a probabilidade de exploração. |
| **Impacto** | **Médio (2)** | O impacto é a perda de controle sobre os dispositivos físicos conectados. Em um cenário de automação residencial, isso pode significar ligar/desligar luzes, abrir portas ou acionar relés de forma indevida. O impacto é limitado aos dispositivos controlados. |
| **Risco** | **Moderado (4)** | O risco é moderado. Embora o impacto possa ser significativo dependendo do que está conectado, a necessidade de acesso à rede local e o impacto limitado (apenas controle de GPIOs) o tornam menos crítico que a indisponibilidade total. |

## 4. Tabela Consolidada de Riscos

A tabela a seguir consolida os ataques analisados, ordenados de forma decrescente pelo nível de Risco (Risco = Probabilidade x Impacto).

| Título do Ataque | Probabilidade (P) | Impacto (I) | Risco (R = P x I) |
| :--- | :--- | :--- | :--- |
| **1. Consumo de Memória (DoS)** | Alta (3) | Alto (3) | **Crítico (9)** |
| **2. Controle Não Autorizado de GPIOs** | Média (2) | Médio (2) | **Moderado (4)** |

**Escala de Risco:**
*   **Baixo:** 1-2
*   **Moderado:** 3-4
*   **Crítico:** 6-9

## 5. Análise Dinâmica (Ir Além)

*Esta seção deve ser preenchida pelo grupo após a realização da montagem em protoboard, compilação do código e teste manual de um dos ataques no ESP32. Favor inserir as capturas de tela, fotos e explicações textuais associadas aqui.*

**Ataque Testado:** [Inserir o título do ataque testado, ex: Consumo de Memória (DoS)]

**Evidências e Explicações:**

[Inserir fotos da montagem em protoboard, capturas de tela do teste de ataque (ex: terminal enviando requisição longa, monitor serial do ESP32) e o texto explicativo dos resultados.]

## 6. Conclusão e Recomendações

O servidor web ESP32 analisado, embora funcional para fins didáticos, apresenta falhas de segurança críticas e moderadas. A vulnerabilidade mais grave é a **falha de limitação de buffer**, que permite um ataque de Negação de Serviço (DoS) com risco **Crítico**. A **falta de autenticação** também representa um risco **Moderado** de controle não autorizado.

**Recomendações de Mitigação:**

1.  **Mitigação do DoS (Vulnerabilidade 2):** Implementar um limite de tamanho para o cabeçalho HTTP lido. Em vez de usar `String header;`, usar um *array* de caracteres (`char header[MAX_HEADER_SIZE];`) com um tamanho máximo definido e verificar se o limite foi excedido durante a leitura.
2.  **Mitigação do Controle Não Autorizado (Vulnerabilidade 1):** Implementar um mecanismo de autenticação simples, como HTTP Basic Authentication, ou utilizar um *token* de sessão (CSRF *token*) na interface web para garantir que apenas requisições legítimas (e não ataques *Cross-Site Request Forgery* - CSRF) sejam processadas.

---
## 7. Referências

[1] [ESP32 Web Server - Arduino IDE | Random Nerd Tutorials](https://randomnerdtutorials.com/esp32-web-server-arduino-ide/)