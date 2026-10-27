from abc import ABC, abstractmethod
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

CENTAVOS = Decimal("0.01")

# Limites superiores inclusivos. A tolerancia (2 h) e o primeiro limite e nao gera credito.
FAIXAS = (
    (timedelta(hours=2), Decimal("0.00")),
    (timedelta(hours=24), Decimal("0.10")),
    (timedelta(hours=72), Decimal("0.25")),
    (None, Decimal("0.50")),
)


def _percentual_base(atraso):
    for limite, percentual in FAIXAS:
        if limite is None or atraso <= limite:
            return percentual


class PoliticaDeCredito(ABC):
    @abstractmethod
    def calcular(self, frete, atraso):
        """Devolve o credito em reais para o frete e o atraso informados."""


class PoliticaPorFaixas(PoliticaDeCredito):
    def __init__(self, multiplicador, teto):
        self._multiplicador = multiplicador
        self._teto = teto

    def calcular(self, frete, atraso):
        percentual = _percentual_base(atraso) * self._multiplicador
        valor = (frete * percentual).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
        return min(valor, self._teto)


class PoliticaCortesia(PoliticaDeCredito):
    def calcular(self, frete, atraso):
        return Decimal("0.00")


class RegistroDePoliticas:
    def __init__(self):
        self._politicas = {}

    def registrar(self, tipo_cliente, politica):
        self._politicas[tipo_cliente] = politica

    def calcular(self, tipo_cliente, frete, atraso):
        return self._politicas[tipo_cliente].calcular(frete, atraso)


def registro_padrao():
    registro = RegistroDePoliticas()
    registro.registrar("VAREJO", PoliticaPorFaixas(Decimal("1"), Decimal("500.00")))
    registro.registrar("CORPORATIVO", PoliticaPorFaixas(Decimal("2"), Decimal("2000.00")))
    registro.registrar("CORTESIA", PoliticaCortesia())
    return registro
