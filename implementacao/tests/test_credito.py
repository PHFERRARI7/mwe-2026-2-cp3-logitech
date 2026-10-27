from datetime import timedelta
from decimal import Decimal

from garantia.credito import calcular_credito


def atraso(horas=0, minutos=0):
    return timedelta(hours=horas, minutes=minutos)


FRETE = Decimal("300.00")


def test_ct01_varejo_atraso_abaixo_da_tolerancia_nao_gera_credito():
    assert calcular_credito("VAREJO", FRETE, atraso(1, 59)) == Decimal("0.00")


def test_ct02_varejo_atraso_de_exatas_2h_ainda_e_tolerancia():
    assert calcular_credito("VAREJO", FRETE, atraso(2, 0)) == Decimal("0.00")
