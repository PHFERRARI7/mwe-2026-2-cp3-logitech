# 5. Uso de assistentes de IA

A dupla usou o assistente **Claude** (Anthropic) durante toda a atividade: leitura do
material da disciplina, rascunho das entregas em `docs/` e condução do ciclo de TDD em
`implementacao/`. O histórico de commits mostra cada ciclo (teste vermelho antes do código).

**Atenção:** as colunas "Decisão da dupla" e "Motivo" abaixo foram preenchidas com o que
foi aplicado no repositório. A dupla deve revisar cada linha, confirmar ou corrigir antes do
envio. Itens marcados "a confirmar pela dupla" ainda não foram validados por uma pessoa.

| Entrega | O que foi pedido | O que o assistente sugeriu | Decisão da dupla | Motivo |
|---|---|---|---|---|
| 1. Domínio | Modelar os contextos e o mapa de contexto para a Garantia de Prazo | Contexto novo "Garantia de Prazo"; dividir o RNF01 em 01a (telemetria) e 01b (confirmação); RF05 na Garantia, não na Telemetria | Aplicado no documento. A confirmar pela dupla | Cada requisito precisa de um único dono; a definição de ausência comprovada é regra de elegibilidade, não dado de telemetria |
| 2. Arquitetura | Escolher protocolos e padrões e justificar | UDP para posição, HTTP/TCP com retentativa e chave idempotente para a confirmação, SSE no portal; Strategy com registro, Adapter (WhatsApp), Decorator (retentativa); `UNIQUE` + `ON CONFLICT DO NOTHING` para o RF09; `SEQUENCE` para o número da nota | Aplicado. A confirmar pela dupla | Cada escolha atende a um requisito citado no documento |
| 2. Arquitetura | Onde não aplicar padrão | **Descartado pelo assistente:** Singleton para o contador de notas (só protege um processo), Strategy por faixa (as faixas são dados, uma tabela basta) e Facade | Descartados | Singleton não resolve concorrência entre instâncias; faixa é dado, não comportamento; Facade não resolveria problema real aqui |
| 3. Testes | Plano com valores-limite, rastreabilidade e dublês | 27 casos (21 unidade, 4 integração, 2 ponta a ponta); limites exatos de 2 h, 24 h e 72 h; Stub, Mock e Spy conforme o que cada caso verifica; mutantes | Aplicado. A confirmar pela dupla | Limites exatos são onde as regras de faixa costumam falhar |
| 4. Portal | Descrever a tela como função do estado | Tipo união discriminado `EstadoTela`, árvore de componentes e origem dos dados (GET + 2 fluxos SSE) | Aplicado. A confirmar pela dupla | Torna cada estado visível e testável |
| 5. Implementação | TDD do RF02 ao RF04 em Python | 9 ciclos com commit de teste antes do commit de código; refatoração final para política por tipo de cliente com registro | Aplicado | Evidência de TDD no histórico; RF04 exige acrescentar tipo sem mexer nos existentes |

## Premissas assumidas pelo assistente (regras de negócio a validar)

Estas premissas foram adotadas para não bloquear a atividade e precisam ser confirmadas com
o professor ou com a dupla:

- Os limites superiores das faixas são inclusivos (2 h exatas ainda é tolerância).
- No Corporativo só os percentuais dobram; a tolerância continua em 2 h.
- O crédito é arredondado para centavos, meio para cima.
- A base de cálculo é o valor do frete.
