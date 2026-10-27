from datetime import timedelta
from decimal import Decimal


def calcular_credito(tipo_cliente, frete, atraso):
    if atraso > timedelta(hours=2):
        return (frete * Decimal("0.10")).quantize(Decimal("0.01"))
    return Decimal("0.00")
