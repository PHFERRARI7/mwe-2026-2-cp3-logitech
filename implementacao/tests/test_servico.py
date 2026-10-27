from datetime import timedelta
from decimal import Decimal
from unittest.mock import Mock

from garantia.servico import ServicoDeGarantia


def test_ct12_cortesia_nao_recebe_credito_mas_e_notificada_do_atraso():
    notificador = Mock()
    servico = ServicoDeGarantia(notificador)

    credito = servico.processar("CORTESIA", Decimal("0.00"), timedelta(hours=30))

    assert credito == Decimal("0.00")
    notificador.notificar_atraso.assert_called_once_with("CORTESIA", timedelta(hours=30))
