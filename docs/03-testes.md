# 3. Plano de testes

## Pirâmide de testes

| Nível | Quantidade de casos | O que cobre |
|---|---|---|
| Unidade | 21 (78%) | Regra de crédito (faixas, limites exatos, teto, tipos de cliente), cálculo do atraso, regra de ausência comprovada, retentativa, Adapter do WhatsApp e componentes do Portal. Rápidos, sem rede e sem banco |
| Integração | 4 (15%) | O que só existe com infraestrutura real: restrição de unicidade do RF09, numeração concorrente do RF06/RNF03 e retomada após falha do Faturamento. Usam PostgreSQL real em contêiner (Testcontainers) |
| Ponta a ponta | 2 (7%) | Fluxo completo com `docker compose up`: confirmação de entrega até nota emitida em 5 min (RNF02) e plataforma saudável com tela ao vivo (RNF04, RF10) |

**Por que essa proporção.** A parte difícil e que muda com frequência é a **regra de cálculo**:
quatro faixas, três tipos de cliente, teto e quatro limites exatos por faixa, o que gera
muitas combinações. Isso só é barato de testar na base da pirâmide, onde cada caso roda em
milissegundos e aponta a linha errada. A camada de integração é pequena, mas **insubstituível**:
unicidade sob concorrência (RF09, RNF03) é propriedade do banco, e um dublê em memória
mentiria sobre ela. Ponta a ponta é caro e lento (sobe 8 serviços), então ficam só dois casos que
nenhum teste menor consegue provar: o prazo de 5 min e a plataforma subindo com um comando.

Regra de bolso adotada: os **valores-limite ficam todos na unidade** (2 h exatas e 2 h 01, 24 h,
72 h, teto), nunca no E2E.

## Casos de teste

Convenções: frete em reais, atraso em horas e minutos. Limites superiores das faixas são
**inclusivos** (2 h exatas ainda está na tolerância).

| ID | Requisito | Pré-condição | Entrada | Resultado esperado | Nível | Dublê | Justificativa do dublê |
|---|---|---|---|---|---|---|---|
| CT01 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 1h59 | Crédito de R$ 0,00 | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT02 | RF02 | Varejo, frete R$ 300,00 | Atraso de 2h00 exatas | Crédito R$ 0,00 (limite da tolerância é inclusivo) | Unidade | Nenhum | Regra pura. É o caso que mata o mutante `>` trocado por `>=` |
| CT03 | RF02 | Varejo, frete R$ 300,00 | Atraso de 2h01 | Crédito R$ 30,00 (10%) | Unidade | Nenhum | Regra pura |
| CT04 | RF02 | Varejo, frete R$ 300,00 | Atraso de 24h00 exatas | Crédito R$ 30,00 (10%, ainda na faixa) | Unidade | Nenhum | Regra pura |
| CT05 | RF02 | Varejo, frete R$ 300,00 | Atraso de 24h01 | Crédito R$ 75,00 (25%) | Unidade | Nenhum | Regra pura |
| CT06 | RF02 | Varejo, frete R$ 300,00 | Atraso de 72h00 exatas | Crédito R$ 75,00 (25%, ainda na faixa) | Unidade | Nenhum | Regra pura |
| CT07 | RF02 | Varejo, frete R$ 300,00 | Atraso de 72h01 | Crédito R$ 150,00 (50%) | Unidade | Nenhum | Regra pura |
| CT08 | RF02 | Varejo, frete R$ 2.000,00 | Atraso de 100h (50% = R$ 1.000,00) | Crédito limitado ao teto: R$ 500,00 | Unidade | Nenhum | Regra pura. Verifica o teto, não o percentual |
| CT09 | RF03 | Corporativo, frete R$ 300,00 | Atraso de 2h00 exatas | Crédito R$ 0,00 (a tolerância **não** dobra, só os percentuais) | Unidade | Nenhum | Regra pura |
| CT10 | RF03 | Corporativo, frete R$ 300,00 | Atraso de 2h01 | Crédito R$ 60,00 (20%, o dobro de 10%) | Unidade | Nenhum | Regra pura |
| CT11 | RF03 | Corporativo, frete R$ 4.000,00 | Atraso de 72h01 (100% = R$ 4.000,00) | Crédito limitado ao teto: R$ 2.000,00 | Unidade | Nenhum | Regra pura. Teto do Corporativo diferente do Varejo |
| CT12 | RF03 | Cortesia, frete R$ 0,00; notificador disponível | Atraso de 30h | Crédito R$ 0,00 **e** uma notificação de atraso enviada | Unidade | **Mock** (`Notificador`) | O que se verifica é um **efeito colateral** (a chamada de notificação ocorreu uma vez), não um valor de retorno: só Mock permite afirmar sobre a chamada |
| CT13 | RF04 | Registro com Varejo, Corporativo e Cortesia; um tipo novo "Premium" registrado em teste | Calcular Varejo (CT03, CT07) e Premium | Resultados do Varejo **idênticos** aos de antes; Premium calculado pela política própria; tipo não registrado lança erro explícito | Unidade | Nenhum | Verifica que acrescentar tipo não altera os existentes; precisa dos objetos reais para provar isso. Equivale ao critério do `git diff` vazio das políticas antigas |
| CT14 | RF01 | Prazo prometido 10:00 | (a) confirmação 12:01; (b) confirmação 09:00 | (a) atraso de 2h01; (b) atraso 0 (nunca negativo) | Unidade | Nenhum | Aritmética de datas pura |
| CT15 | RF05 | Ausência registrada às 15:00 | Telemetria informa veículo a **200 m exatos** por **10 min exatos** | Sem crédito (ausência comprovada; limites inclusivos) | Unidade | **Stub** (`ClienteDeTelemetria`) | A regra só precisa de uma resposta pré-programada da telemetria; não interessa como a telemetria chegou a ela |
| CT16 | RF05 | Ausência registrada às 15:00 | Veículo a **201 m** por 12 min | Crédito normal (fora do raio) | Unidade | **Stub** (`ClienteDeTelemetria`) | Mesmo motivo: resposta fixa de entrada |
| CT17 | RF05 | Ausência registrada às 15:00 | Veículo a 150 m por **9min59** | Crédito normal (permanência insuficiente) | Unidade | **Stub** (`ClienteDeTelemetria`) | Mesmo motivo: resposta fixa de entrada |
| CT18 | RF09 | Banco real vazio; Faturamento com dublê | A mesma confirmação de entrega enviada **duas vezes em sequência** | Uma linha em `creditos`; Faturamento chamado **uma** vez; segunda resposta devolve o crédito existente | Integração | **Mock** (`ClienteDeFaturamento`) + banco real | Precisa afirmar que a nota **não** foi pedida de novo (contagem de chamadas = Mock). O banco é real porque a unicidade é dele |
| CT19 | RF09 | Banco real vazio | A mesma confirmação enviada por **20 threads ao mesmo tempo** | Exatamente 1 crédito e 1 pedido de nota | Integração | Nenhum (banco real) | Concorrência só aparece contra o banco de verdade. Um repositório em memória daria resultado enganoso |
| CT20 | RF06, RNF03 | Faturamento com PostgreSQL real | **1.000 emissões concorrentes** de nota de crédito | 1.000 números **distintos** e crescentes; nenhuma violação do índice único | Integração | Nenhum (banco real) | A garantia é da `SEQUENCE`/índice do banco; dublê esconderia o defeito |
| CT21 | RF08 | Canal que falha sempre | Enviar uma notificação por `ComRetentativa(max=3)` | Canal chamado **4 vezes** (1 + 3 retentativas); a falha final fica **registrada** (estado `FALHA_FINAL`), não engolida | Unidade | **Spy** sobre o canal (Stub que falha) | O Decorator real deve rodar de verdade; o Spy só **observa** quantas vezes o canal foi chamado |
| CT22 | RF08 | Canal que falha 2 vezes e depois funciona | Enviar a notificação | Sucesso na 3ª chamada; nenhuma falha final registrada; tentativas = 3 | Unidade | **Stub** (respostas em sequência) | Basta uma sequência pré-programada de falha, falha, sucesso |
| CT23 | RF07 | Cliente com canal preferido WhatsApp | Notificar atraso | O Adapter envia ao parceiro exatamente o **formato do parceiro** (campos traduzidos), e não o formato interno | Unidade | **Mock** (cliente HTTP do parceiro) | O que importa é o **conteúdo da requisição** enviada; Mock permite conferir o payload |
| CT24 | RF10 | Pedido entregue com atraso, crédito de R$ 75,00 no saldo | Renderizar `AcompanhamentoPedido` | Mostra "Entregue com atraso", a previsão original e saldo R$ 75,00 | Unidade | **Stub** (hooks de API) | A tela é função do estado; fornece-se o estado pronto e verifica-se o que é exibido |
| CT25 | RF09, RNF02 | Banco real; Faturamento indisponível na 1ª chamada | Confirmação de entrega; depois o Faturamento volta | Crédito em `PENDENTE_NOTA`; retomada emite **uma** nota e muda para `EMITIDO` | Integração | **Stub** (Faturamento: falha e depois responde) + banco real | Simula a indisponibilidade com resposta pré-programada; o estado persistido tem de ser real |
| CT26 | RNF02, RF06 | Plataforma completa no Compose | Pedido confirmado como entregue com atraso de 30h | Nota de crédito emitida e cliente notificado em **até 5 min** | Ponta a ponta | Nenhum | O requisito é de tempo entre componentes reais |
| CT27 | RNF04, RF10 | Redes e volumes externos criados | `docker compose up -d --build --wait` | Todos os serviços `healthy`; Portal exibe a posição do veículo e a atualiza sem recarregar | Ponta a ponta | Nenhum | Prova que o conjunto sobe com um comando e que o SSE chega ao navegador |

Rastreabilidade (requisito → casos): RF01 → CT14 · RF02 → CT01-CT08 · RF03 → CT09-CT12 ·
RF04 → CT13 · RF05 → CT15-CT17 · RF06 → CT20, CT26 · RF07 → CT23 · RF08 → CT21, CT22 ·
RF09 → CT18, CT19, CT25 · RF10 → CT24, CT27 · RNF01 → ver abaixo · RNF02 → CT25, CT26 ·
RNF03 → CT20 · RNF04 → CT27.

**RNF01** (UDP tolera perda; confirmação não tolera) é decisão de arquitetura, verificada por
revisão do protocolo escolhido (UDP para posição, HTTP/TCP com retentativa e chave idempotente
para a confirmação) e pelo CT18/CT19, que provam que reenvios da confirmação são seguros.

## Mutante que o plano detecta

| Mutante | Caso que o detecta | Por quê |
|---|---|---|
| Na tolerância, trocar `atraso > 2h` por `atraso >= 2h` | **CT02** (Varejo, 2h00 exatas deveria dar R$ 0,00) | O mutante passaria a conceder 10% a quem atrasou exatamente 2 h, e o resultado sairia R$ 30,00 em vez de R$ 0,00. CT01 (1h59) e CT03 (2h01) **não** pegam esse mutante, e é por isso que o limite exato existe |
| Trocar `min(valor, teto)` por `max(valor, teto)` | **CT08** e **CT11** | CT08 devolveria R$ 1.000,00 em vez de R$ 500,00; CT11 devolveria R$ 4.000,00 em vez de R$ 2.000,00. Os casos sem teto (CT03 a CT07) continuariam verdes e não detectariam |
| Corporativo dobrar também a tolerância (2 h vira 4 h) | **CT09** e **CT10** | CT10 (2h01 deveria dar R$ 60,00) devolveria R$ 0,00 |
| Remover o `UNIQUE (chave_de_entrega)` ou trocar `ON CONFLICT DO NOTHING` por inserção direta | **CT19** (e CT18) | A duplicata criaria um segundo crédito; só um teste com banco real e concorrência vê isso |
| Contador de nota em variável de processo em vez de `SEQUENCE` | **CT20** | Com concorrência real, números se repetem e o índice único recusa |
