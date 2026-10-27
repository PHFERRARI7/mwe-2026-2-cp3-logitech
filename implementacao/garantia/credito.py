from datetime import timedelta
from decimal import Decimal

TETO_VAREJO = Decimal("500.00")


def calcular_credito(tipo_cliente, frete, atraso):
    if atraso > timedelta(hours=72):
        percentual = Decimal("0.50")
    elif atraso > timedelta(hours=24):
        percentual = Decimal("0.25")
    elif atraso > timedelta(hours=2):
        percentual = Decimal("0.10")
    else:
        return Decimal("0.00")
    return min((frete * percentual).quantize(Decimal("0.01")), TETO_VAREJO)
