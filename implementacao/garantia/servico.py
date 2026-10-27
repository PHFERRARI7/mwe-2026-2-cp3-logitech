from garantia.credito import calcular_credito


class ServicoDeGarantia:
    def __init__(self, notificador):
        self._notificador = notificador

    def processar(self, tipo_cliente, frete, atraso):
        credito = calcular_credito(tipo_cliente, frete, atraso)
        if tipo_cliente == "CORTESIA":
            self._notificador.notificar_atraso(tipo_cliente, atraso)
        return credito
