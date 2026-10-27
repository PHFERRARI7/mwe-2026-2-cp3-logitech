from garantia.politicas import registro_padrao

_REGISTRO = registro_padrao()


def calcular_credito(tipo_cliente, frete, atraso):
    return _REGISTRO.calcular(tipo_cliente, frete, atraso)
