from datetime import timedelta


def calcular_atraso(prazo_prometido, confirmacao_de_entrega):
    return max(confirmacao_de_entrega - prazo_prometido, timedelta(0))
