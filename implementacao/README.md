# 5. Implementação em TDD

Implementem a regra de cálculo do crédito (RF02, RF03 e RF04) em **uma** linguagem à
escolha da dupla: Java, C#, Python ou TypeScript. O Codespace deste repositório já traz
as quatro.

## Como trabalhar

1. Escrevam um teste para um caso do plano (`docs/03-testes.md`) e confirmem que ele
   **falha**. Façam o commit: `test: CT01 atraso abaixo da tolerância não gera crédito`.
2. Escrevam o mínimo de código que faz o teste passar. Façam o commit:
   `feat: calcula crédito zero dentro da tolerância`.
3. Se for preciso, refatorem com os testes passando. Façam o commit: `refactor: ...`.
4. Repitam para o próximo caso.

O histórico de commits é a evidência do TDD: o commit de teste vem antes do commit de
código que o faz passar.

## O que registrar aqui

- Linguagem e framework de teste: Python 3 e pytest. Dinheiro em `Decimal` (arredondamento
  `ROUND_HALF_UP` para centavos) e atraso em `timedelta`.
- Comando para executar os testes: `cd implementacao && python3 -m pytest -v`
- Casos do plano implementados (IDs): CT01 a CT14 (CT01-CT08 = RF02, CT09-CT12 = RF03,
  CT13 = RF04, CT14 = RF01). Os demais casos (CT15 em diante) dependem de banco, rede ou
  telas e ficam fora desta implementação.
- Estrutura: `garantia/atraso.py` (RF01), `garantia/politicas.py` (faixas, política por tipo
  de cliente e registro extensível), `garantia/credito.py` (função de entrada),
  `garantia/servico.py` (Cortesia notificada).
- Saída da última execução dos testes:

```
============================= test session starts ==============================
platform linux -- Python 3.13.18, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /home/claude/mwe-2026-2-cp3-logitech/implementacao
configfile: pytest.ini
testpaths: tests
plugins: platformdirs-4.13.0, anyio-4.15.1
collecting ... collected 15 items

tests/test_atraso.py::test_ct14a_confirmacao_depois_do_prazo_gera_atraso_pela_diferenca PASSED [  6%]
tests/test_atraso.py::test_ct14b_confirmacao_antes_do_prazo_nunca_gera_atraso_negativo PASSED [ 13%]
tests/test_credito.py::test_ct01_varejo_atraso_abaixo_da_tolerancia_nao_gera_credito PASSED [ 20%]
tests/test_credito.py::test_ct02_varejo_atraso_de_exatas_2h_ainda_e_tolerancia PASSED [ 26%]
tests/test_credito.py::test_ct03_varejo_acima_de_2h_recebe_10_por_cento_do_frete PASSED [ 33%]
tests/test_credito.py::test_ct04_varejo_24h_exatas_continua_na_faixa_de_10_por_cento PASSED [ 40%]
tests/test_credito.py::test_ct05_varejo_acima_de_24h_recebe_25_por_cento PASSED [ 46%]
tests/test_credito.py::test_ct06_varejo_72h_exatas_continua_na_faixa_de_25_por_cento PASSED [ 53%]
tests/test_credito.py::test_ct07_varejo_acima_de_72h_recebe_50_por_cento PASSED [ 60%]
tests/test_credito.py::test_ct08_varejo_credito_nunca_passa_do_teto_de_500 PASSED [ 66%]
tests/test_credito.py::test_ct09_corporativo_tolerancia_de_2h_nao_dobra PASSED [ 73%]
tests/test_credito.py::test_ct10_corporativo_percentuais_dobram_acima_de_2h PASSED [ 80%]
tests/test_credito.py::test_ct11_corporativo_credito_nunca_passa_do_teto_de_2000 PASSED [ 86%]
tests/test_politicas.py::test_ct13_novo_tipo_nao_altera_os_existentes_e_tipo_desconhecido_falha PASSED [ 93%]
tests/test_servico.py::test_ct12_cortesia_nao_recebe_credito_mas_e_notificada_do_atraso PASSED [100%]

============================== 15 passed in 0.03s ==============================
```
