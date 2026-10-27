from datetime import datetime, timedelta

from garantia.atraso import calcular_atraso

PRAZO = datetime(2026, 10, 27, 10, 0)


def test_ct14a_confirmacao_depois_do_prazo_gera_atraso_pela_diferenca():
    assert calcular_atraso(PRAZO, datetime(2026, 10, 27, 12, 1)) == timedelta(hours=2, minutes=1)


def test_ct14b_confirmacao_antes_do_prazo_nunca_gera_atraso_negativo():
    assert calcular_atraso(PRAZO, datetime(2026, 10, 27, 9, 0)) == timedelta(0)
