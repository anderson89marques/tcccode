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

# Classes de dominio ///////////////////////////////
class ArquivoAdquirente(object):
    def __init__(self):
        self.nome = None
        self.destinatario = None
        self.cadeia = None
        self.adquirente = None
        self.extrato = None
        self.dataArquivo = None
        self.dataCRiacao = None
        self.periodoInicial = None
        self.periodoFinal = None
        self.tipoProcessamento = None
        self.dataProcessamento = None
        self.versao = None
        self.lote = None
        self.conteudo = None
        self.tipo = None

    """
        sobrescrevi o metodo setitem para tratar o objeto como dicionario.
        e todo objeto python tem um metodo dict e atraves dele acesso os atributos cmo se fossem chaves de um dicionario.

        e ao fazer Arquivo['nome_atributo'] = valor, faz o mesmo que Arquivo.nome_atributo = valor.
        A vantagem da nova abordagem e que posso iterar em dicionario com as chaves sendo os nomes dos atributos e atribuir seus valores para o
        objeto.
        ou seja, posso construir um objeto a partir de um diconario.

        OBS IMPORTANTE:
            PODE SER LEGAL PASSAR O DICIONARIO COMO PARAMETRO E CONSTRUIR O OBJETO, OU SEJA MONTAR O OBJETO COM FAZENDO A ITERACAO SOBRE OS ATRBUTOS
            INTERNAMENTE E NAO EXTERNAMENTE.
    """
    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return "Adq:%r per. Ini:%r per. Fin:%r tipoProc:%r dataProc:%r desti:%r cadeia:%r tipo: %r" % (self.adquirente, self.periodoInicial, self.periodoFinal, self.tipoProcessamento,
                self.dataProcessamento, self.destinatario, self.cadeia, self.tipo)

class ProdutoAdquirente(object):
    def __init__(self):
        self.nome = None
        self.bandeira = None
        self.debito = None
        self.credito = None

    def __repr__(self):
        return "nome: %r, bandeira: %r" % (self.nome, self.bandeira)


class RegistroAdquirente(object):
    def __init__(self):
        self.arquivo = None
        self.statusConsolidacao = StatusConsolidacao.PENDENTE


class LoteAdquirente(RegistroAdquirente):
    def __init__(self):
        RegistroAdquirente.__init__(self)
        self.cnpj = None
        self.estabelecimento = None
        self.terminal = None
        self.loteAutorizador = None
        self.loteFinanceiro = None
        self.dataProcessamento = None
        self.dataPagamentoPrevista = None
        self.tipoTransacao = None
        self.produto = None
        self.parcela = None
        self.totalParcelas = None
        self.valorBruto = None
        self.valorTaxaDesconto = None
        self.valorLiquido = None
        self.descricao = None

    def __repr__(self):
        return "cnpj:%r, estab.: %r, loteFin: %r, loteAut: %r, arquivo: %r tipoTrans: %r" % (self.cnpj, self.estabelecimento, self.loteFinanceiro,
                                                                               self.loteAutorizador, self.arquivo, self.tipoTransacao)


class LoteVendaAdquirente(LoteAdquirente):
    def __init__(self, propriedades=None):
        LoteAdquirente.__init__(self)
        if propriedades is not None:
            for key, value in propriedades.items():
                self.__dict__[key] = value


class LoteParceladoFuturoAdquirente(LoteAdquirente):
    def __init__(self, propriedades=None):
        LoteAdquirente.__init__(self)
        self.loteVenda = None

        if propriedades is not None:
            for key, value in propriedades.items():
                self.__dict__[key] = value


class RegistroVendaAdquirente(RegistroAdquirente):
    def __init__(self):
        self.estabelecimento = None


class TransacaoAdquirente(RegistroVendaAdquirente):
    def __init__(self, propriedades=None):
        RegistroAdquirente.__init__(self)
        self.lote = None
        self.terminal = None
        self.loteAutorizador = None
        self.loteFinanceiro = None
        self.data = None
        self.dataTransacao = None
        self.tipoTransacao = None
        self.produto = None
        self.parcela = None
        self.totalParcelas = None
        self.valorTotal = None
        self.valorParcela = None
        self.valorTaxaDesconto = None
        self.valorLiquido = None
        self.taxaDesconto = None
        self.tarifa = None
        self.cartao = None
        self.codigoAutorizacao = None
        self.nsu = None
        self.itrn = None
        self.modoCaptura = None
        self.descricao = None

        if propriedades is not None:
            for key, value in propriedades.items():
                self.__dict__[key] = value

    def __repr__(self):
        return "Lote:%r, terminal: %r, loteFin: %r, loteAut: %r, " \
               "arquivo: %r tipoTrans: %r" % (self.lote, self.terminal, self.loteFinanceiro,
                                              self.loteAutorizador, self.arquivo, self.tipoTransacao)


class Icpt(RegistroVendaAdquirente):
    def __init__(self, propriedades=None):
        RegistroVendaAdquirente.__init__(self)
        self.lote = None
        self.valorIntercambio = None
        self.valorTaxaBandeira = None
        self.valorMargem = None
        self.nsu = None
        self.itrn = None
        self.tipoCartao = None
        self.codigoDescricao = None
        self.transacao = None

        if propriedades is not None:
            for key, value in propriedades.items():
                self.__dict__[key] = value

    def __repr__(self):
        return "Lote: %r, Val.Int: %r, Val.Tax: %r, Val.Mar: %r, nsu: %r, itrn: %r, tipoCartao: %r, codigoDes: %r, " \
               "trans: %r" % (self.lote, self.valorIntercambio, self.valorTaxaBandeira, self.valorMargem, self.nsu,
                              self.itrn, self.tipoCartao, self.codigoDescricao, self.transacao)