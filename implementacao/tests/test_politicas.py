from datetime import timedelta
from decimal import Decimal

import pytest

from garantia.politicas import PoliticaDeCredito, RegistroDePoliticas, registro_padrao

FRETE = Decimal("300.00")


class PoliticaPremium(PoliticaDeCredito):
    """Tipo novo definido apenas no teste: nao existe no codigo de producao."""

    def calcular(self, frete, atraso):
        return Decimal("42.00")


def test_ct13_novo_tipo_nao_altera_os_existentes_e_tipo_desconhecido_falha():
    registro = registro_padrao()
    varejo_antes = (
        registro.calcular("VAREJO", FRETE, timedelta(hours=2, minutes=1)),
        registro.calcular("VAREJO", FRETE, timedelta(hours=72, minutes=1)),
    )

    registro.registrar("PREMIUM", PoliticaPremium())

    assert registro.calcular("PREMIUM", FRETE, timedelta(hours=3)) == Decimal("42.00")
    assert varejo_antes == (Decimal("30.00"), Decimal("150.00"))
    assert registro.calcular("VAREJO", FRETE, timedelta(hours=2, minutes=1)) == Decimal("30.00")
    assert registro.calcular("VAREJO", FRETE, timedelta(hours=72, minutes=1)) == Decimal("150.00")
    with pytest.raises(KeyError):
        registro.calcular("INEXISTENTE", FRETE, timedelta(hours=3))
