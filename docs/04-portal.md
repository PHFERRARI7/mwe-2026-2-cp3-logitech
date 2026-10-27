# 4. Tela do Portal do Cliente (RF10)

A tela de acompanhamento é uma **função do estado**: `tela = f(estado)`. O hook
`useAcompanhamento(pedidoId)` reúne as três fontes (status do pedido, posição ao vivo, saldo de
créditos) em **um único valor** de um tipo união discriminado, e os componentes só desenham
esse valor. Nenhum componente decide por conta própria "está carregando" ou "deu erro".

```ts
type EstadoTela =
  | { tipo: 'carregando' }
  | { tipo: 'erro'; mensagem: string; podeTentarDeNovo: boolean }
  | { tipo: 'nao-encontrado' }
  | { tipo: 'aguardando-coleta'; pedido: Pedido; previsao: Previsao }
  | { tipo: 'em-transito'; pedido: Pedido; posicao: Posicao; previsao: Previsao; ao_vivo: boolean }
  | { tipo: 'em-transito-em-risco'; pedido: Pedido; posicao: Posicao; previsao: Previsao; ao_vivo: boolean }
  | { tipo: 'entregue-no-prazo'; pedido: Pedido; entregueEm: string; saldo: Saldo }
  | { tipo: 'entregue-com-credito'; pedido: Pedido; entregueEm: string; atrasoHoras: number; credito: Credito; saldo: Saldo }
  | { tipo: 'entregue-sem-credito'; pedido: Pedido; entregueEm: string; atrasoHoras: number; motivo: 'tolerancia' | 'ausencia-comprovada' | 'cortesia'; saldo: Saldo };
```

## Estados da tela

`ao_vivo` indica se o fluxo SSE está conectado. Quando a telemetria para de chegar (a perda de
pacotes é tolerada pelo RNF01a), a **última posição conhecida continua na tela, marcada como
desatualizada**, em vez de sumir.

| Estado | Dados disponíveis | O que a tela exibe |
|---|---|---|
| `carregando` | Nenhum (aguardando o status inicial) | Esqueleto (placeholders) no lugar do mapa, da previsão e do saldo. Nenhum valor numérico, para não parecer R$ 0,00 |
| `erro` | Mensagem; se dá para tentar de novo | Aviso de falha e botão "Tentar novamente". Se o saldo falhou mas o pedido carregou, mostra o pedido e só o bloco do saldo com erro (falha parcial não derruba a tela) |
| `nao-encontrado` | Nenhum | "Pedido não encontrado", com orientação para conferir o número |
| `aguardando-coleta` | Pedido e previsão de chegada | Status "Aguardando coleta", previsão de chegada, **sem mapa** (ainda não há posição) |
| `em-transito` | Pedido, posição do veículo, previsão, `ao_vivo` | Mapa com o veículo, hora da última atualização, previsão de chegada dentro do prazo prometido, selo "Ao vivo". Se `ao_vivo` for falso ou a posição tiver mais de 90 s (3 batidas de 30 s perdidas), selo "Desatualizado há X" |
| `em-transito-em-risco` | Igual ao anterior; a previsão passa do prazo prometido | Igual a `em-transito`, mais o aviso "A entrega pode atrasar. A Garantia de Prazo está ativa" e o prazo prometido destacado |
| `entregue-no-prazo` | Pedido, instante da entrega, saldo | "Entregue no prazo", data e hora, saldo de créditos |
| `entregue-com-credito` | Pedido, entrega, atraso em horas, crédito (valor, percentual, número da nota), saldo | "Entregue com atraso de X h", crédito concedido de R$ Y (número da nota de crédito) e saldo **atualizado ao vivo** quando a nota é emitida (pode chegar até 5 min depois da entrega) |
| `entregue-sem-credito` | Pedido, entrega, atraso, **motivo** (`tolerancia`, `ausencia-comprovada`, `cortesia`), saldo | "Entregue com atraso de X h" e a **razão** do crédito não existir: dentro da tolerância de 2 h, ausência comprovada, ou frete cortesia. O cliente nunca fica sem explicação |

Estado transitório dentro de `entregue-*`: entre a confirmação e a emissão da nota (até 5 min,
RNF02) o bloco do crédito mostra "Calculando crédito" e é substituído pelo SSE do saldo.

## Árvore de componentes

```
<AcompanhamentoPedido pedidoId>            // contêiner: chama useAcompanhamento e escolhe a visão
  ├─ <EstadoCarregando />
  ├─ <EstadoErro mensagem podeTentarDeNovo onTentarDeNovo />
  ├─ <EstadoNaoEncontrado />
  └─ <VisaoDoPedido pedido estado>
       ├─ <CabecalhoPedido numero status cliente />
       ├─ <MapaPosicao posicao atualizadaEm desatualizada />       // só em trânsito
       ├─ <PrevisaoChegada previsao prazoPrometido emRisco />
       ├─ <AvisoGarantia emRisco />                                 // só em risco
       └─ <ResumoEntrega entregueEm atrasoHoras motivoSemCredito />  // só entregue
            └─ <BlocoCredito credito calculando />
       └─ <SaldoCreditos saldo carregando erro />
```

| Componente | Props recebidas | Responsabilidade |
|---|---|---|
| `AcompanhamentoPedido` | `pedidoId` | Único componente com estado e efeitos. Usa `useAcompanhamento`, devolve a visão conforme `estado.tipo`. Cancela os fluxos SSE ao desmontar (função de limpeza do `useEffect`) |
| `EstadoCarregando` | nenhuma | Esqueleto. Sem dados |
| `EstadoErro` | `mensagem`, `podeTentarDeNovo`, `onTentarDeNovo` | Mostra a falha e dispara nova tentativa |
| `EstadoNaoEncontrado` | nenhuma | Mensagem de pedido inexistente |
| `VisaoDoPedido` | `pedido`, `estado` | Monta os blocos que existem para aquele estado |
| `CabecalhoPedido` | `numero`, `status`, `cliente` | Identificação e status do pedido |
| `MapaPosicao` | `posicao` (lat, lon), `atualizadaEm`, `desatualizada` | Desenha o veículo e o selo "Ao vivo" ou "Desatualizado há X" |
| `PrevisaoChegada` | `previsao`, `prazoPrometido`, `emRisco` | Hora prevista e o prazo prometido, com destaque se a previsão ultrapassa o prazo |
| `AvisoGarantia` | `emRisco` | Mensagem da Garantia de Prazo quando há risco de atraso |
| `ResumoEntrega` | `entregueEm`, `atrasoHoras`, `motivoSemCredito` | Resultado da entrega e, se houve atraso sem crédito, o motivo |
| `BlocoCredito` | `credito`, `calculando` | Valor, percentual e número da nota; "Calculando crédito" enquanto a nota não saiu |
| `SaldoCreditos` | `saldo`, `carregando`, `erro` | Soma dos créditos. Tem seu próprio estado de falha parcial |

Todos os componentes abaixo do contêiner são **puros**: mesma prop, mesma tela. Isso é o que
permite testá-los com Testing Library apenas fornecendo o estado (CT24).

## Origem dos dados

| Dado da tela | Origem | Como chega ao navegador |
|---|---|---|
| Pedido e status (`aguardando-coleta`, `em-transito`, `entregue`) | Serviço **Pedidos**, `GET /api/v1/pedidos/{id}/status` | HTTP (`fetch`) na montagem; novo `GET` após o evento de saldo, para detectar a entrega |
| Previsão de chegada e prazo prometido | Serviço **Frete** (prazo prometido) exposto via Pedidos/Garantia no `GET` do pedido | HTTP na montagem |
| Posição do veículo | **Telemetria** (painel): `GET /api/v1/posicoes` para o estado inicial e `GET /api/v1/eventos` para o fluxo | **SSE** (`EventSource`), evento `posicao`. O navegador reconecta sozinho. O hook marca `ao_vivo = false` no evento `error` e `desatualizada` se a última posição tiver mais de 90 s |
| Crédito do pedido, atraso e motivo | Serviço **Garantia**, `GET /api/v1/pedidos/{id}/garantia` | HTTP na montagem e ao receber o evento de saldo |
| Saldo de créditos | Serviço **Garantia**, `GET /api/v1/clientes/{id}/creditos` | HTTP para o saldo inicial; **SSE** `GET /api/v1/clientes/{id}/creditos/eventos` para as mudanças (evento `credito-emitido`) |

Atualização ao vivo, em resumo: **dois fluxos SSE** (posição e saldo), abertos quando o
componente monta e fechados quando ele desmonta. O estado inicial vem por `GET`, e os eventos só
acrescentam mudanças, o que evita tela vazia até o primeiro evento.

Cuidados da plataforma que valem para esta tela:

- **CORS:** Pedidos, Garantia e o painel precisam listar `http://localhost:5173` em
  `LOGITECH_CORS_ORIGINS`. O sintoma de esquecer é tela vazia sem erro de rede aparente.
- **Autorização:** com `LOGITECH_AUTH_ATIVA=true`, o token Bearer do usuário vai nos `GET`.
  O `EventSource` nativo não envia cabeçalho `Authorization`; nesse caso o fluxo usa
  `fetch` com leitura do corpo em stream, ou um cookie de sessão. Registrado como risco.
- **Pedidos de outro cliente:** o filtro por dono do pedido é feito no **backend**; a tela
  esconder a informação não protege nada.
