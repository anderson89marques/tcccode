__author__ = 'anderson'
from enum import Enum


# Enums /////////////////////////////////////////
class TipoProcessamentoAdquirente(Enum):
    SUBMISSAO = "Submissao"
    REPROCESSAMENTO = "Re-processamento"


class TipoArquivo(Enum):
    ARQUIVO_VENDA_ADQUIRENTE = "arquivo de venda adiquirente"


class StatusArquivo(Enum):
    PENDENTE = "Pendente"
    PROCESSADO_OK = "Processado"


class StatusConsolidacao(Enum):
    PENDENTE = "Pendente"


class TipoTransacao(Enum):
    VENDA = "Venda"
    AJUSTE = "Ajuste"
    TARIFA = "Tarifa"
    CHARGEBACK = "Chargeback"
    CANCELAMENTO = "Cancelamento"
    ACELERACAO = "Aceleracao"
    REENTRADA = "Reentrada"


class ModoCaptura(Enum):
    pass
