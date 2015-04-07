from sqlalchemy import (
    Column, Index, Integer, BigInteger,
    Text, Date, String,
    DECIMAL, ForeignKey
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session, sessionmaker,
    relationship, backref
    )

from zope.sqlalchemy import ZopeTransactionExtension
from Enums import StatusConsolidacao

#exprime_on_commit  usado pra que nao de o erro de detached na hora usa os objetos depois de serem buscados no banco.
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), expire_on_commit=False))
Base = declarative_base()


#Index('my_index', MyModel.name, unique=True, mysql_length=255)

# Classes de dominio ///////////////////////////////
class ArquivoAdquirente(Base):
    __tablename__ = 'arquivo_adquirente'
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    destinatario = Column(Text)
    cadeia = Column(Text)
    adquirente = Column(Text)
    extrato = Column(Text)
    data_arquivo = Column(Date)
    data_criacao = Column(Date)
    periodo_inicial = Column(Date)
    periodo_final = Column(Date)
    tipo_processamento = Column(Text)
    data_processamento = Column(Text)
    versao = Column(Text)
    conteudo = Column(Text)
    tipo = Column(Text)

    def __init__(self):
        self.nome = None
        self.destinatario = None
        self.cadeia = None
        self.adquirente = None
        self.extrato = None
        self.data_arquivo = None
        self.data_criacao = None
        self.periodo_inicial = None
        self.periodo_final = None
        self.tipo_processamento = None
        self.data_processamento = None
        self.versao = None
        #self.lote = None
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
        return "Adq:%r per. Ini:%r per. Fin:%r tipoProc:%r dataProc:%r desti:%r cadeia:%r tipo: %r" % (self.adquirente, self.periodo_inicial, self.periodo_final, self.tipo_processamento,
                self.data_processamento, self.destinatario, self.cadeia, self.tipo)


class RegistroAdquirente(Base):
    __tablename__ = 'registro_adquirente'
    id = Column(Integer, primary_key=True)
    arquivo_id = Column(Integer, ForeignKey('arquivo_adquirente.id'))
    arquivo = relationship("ArquivoAdquirente")
    status_consolidacao = Column(Text)

    type = Column(String(50)) #aqui e que vai ser escrito qual e a classe na tabela

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'registro_adquirente'

    }

    def __init__(self):
        self.arquivo = None
        self.status_consolidacao = StatusConsolidacao.PENDENTE.value


class LoteAdquirente(RegistroAdquirente):
    cnpj = Column(Text)
    estabelecimento = Column(Text)
    terminal = Column(Text)
    lote_autorizador = Column(BigInteger)
    lote_financeiro = Column(BigInteger)
    data_processamento = Column(Date)
    data_pagamento_prevista = Column(Date)
    tipo_transacao = Column(Text)
    produto = Column(Text)
    parcela = Column(Integer)
    total_parcelas = Column(Integer)
    valor_bruto = Column(DECIMAL)
    valor_taxa_desconto = Column(DECIMAL)
    valor_liquido = Column(DECIMAL)
    descricao = Column(Text)

    #para identificar a classe na tabela
    __mapper_args__ = {
        'polymorphic_identity': 'LoteAdquirente'
    }

    def __init__(self):
        RegistroAdquirente.__init__(self)
        self.cnpj = None
        self.estabelecimento = None
        self.terminal = None
        self.lote_autorizador = None
        self.lote_financeiro = None
        self.data_processamento = None
        self.data_pagamento_prevista = None
        self.tipo_transacao = None
        self.produto = None
        self.parcela = None
        self.total_parcelas = None
        self.valor_bruto = None
        self.valor_taxa_desconto = None
        self.valor_liquido = None
        self.descricao = None

    def __repr__(self):
        return "cnpj:%r, estab.: %r, loteFin: %r, loteAut: %r, arquivo: %r tipoTrans: %r" % (self.cnpj, self.estabelecimento, self.lote_financeiro,
                                                                               self.lote_autorizador, self.arquivo, self.tipo_transacao)

class LoteVendaAdquirente(LoteAdquirente):
    __mapper_args__ = {
        'polymorphic_identity': 'LoteVendaAdquirente'
    }

    def __init__(self, propriedades=None):
        LoteAdquirente.__init__(self)
        if propriedades is not None:
            for key, value in propriedades.items():
                self.__dict__[key] = value


class LoteParceladoFuturoAdquirente(LoteAdquirente):
    lote_venda_id = Column(Integer, ForeignKey('registro_adquirente.id'))
    #pra fazer um pra um, mais so um lado sabe do outro e fazer a referencia para a proria tabela remote_side=[RegistroAdquirente.id],
    lote_venda = relationship('LoteVendaAdquirente', uselist=False, remote_side=[RegistroAdquirente.id])

    __mapper_args__ = {
        'polymorphic_identity': 'LoteParceladoFuturoAdquirente'
    }

    def __init__(self, propriedades=None):
        LoteAdquirente.__init__(self)
        self.lote_venda = None

        if propriedades is not None:
            for key, value in propriedades.items():
                self.__dict__[key] = value


    def __repr__(self):
        return ":::: LoteVenda >>>>>: %r" % self.lote_venda


class RegistroVendaAdquirente(Base):
    __tablename__ = 'registro_venda_adquirente'
    id = Column(Integer, primary_key=True)
    estabelecimento = Column(Text)
    arquivo_id = Column(Integer, ForeignKey('arquivo_adquirente.id'))
    arquivo = relationship("ArquivoAdquirente")
    lote_id = Column(Integer, ForeignKey('registro_adquirente.id'))
    lote = relationship("LoteVendaAdquirente", uselist=False) #pra fazer um pra um, mais so um lado sabe do outro.
    status_consolidacao = Column(Text)
    nsu = Column(BigInteger)
    itrn = Column(BigInteger)
    type = Column(String(50)) #aqui e que vai ser escrito qual e a classe na tabela

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'registro_venda_adquirente'

    }

    def __init__(self):
        self.arquivo = None
        self.status_consolidacao = StatusConsolidacao.PENDENTE.value
        self.estabelecimento = None
        self.nsu = None
        self.itrn = None


class TransacaoAdquirente(RegistroVendaAdquirente):
    terminal = Column(Text)
    lote_autorizador = Column(BigInteger)
    lote_financeiro = Column(BigInteger)
    data = Column(Date)
    data_transacao = Column(Date)
    tipo_transacao = Column(Text)
    produto = Column(Text)
    parcela = Column(Integer)
    total_parcelas = Column(Integer)
    valor_total = Column(DECIMAL)
    valor_parcela = Column(DECIMAL)
    valor_taxa_desconto = Column(DECIMAL)
    valor_liquido = Column(DECIMAL)
    taxa_desconto = Column(DECIMAL)
    tarifa = Column(DECIMAL)
    cartao = Column(Text)
    codigo_autorizacao = Column(Text)
    modo_captura = Column(Text)
    descricao = Column(Text)


    __mapper_args__ = {
        'polymorphic_identity': 'TransacaoAdquirente'
    }

    def __init__(self, propriedades=None):
        RegistroVendaAdquirente.__init__(self)
        self.lote = None
        self.terminal = None
        self.lote_autorizador = None
        self.lote_financeiro = None
        self.data = None
        self.data_transacao = None
        self.tipo_transacao = None
        self.produto = None
        self.parcela = None
        self.total_parcelas = None
        self.valor_total = None
        self.valor_parcela = None
        self.valor_taxa_desconto = None
        self.valor_liquido = None
        self.taxa_desconto = None
        self.tarifa = None
        self.cartao = None
        self.codigo_autorizacao = None
        self.nsu = None
        self.itrn = None
        self.modo_captura = None
        self.descricao = None

        if propriedades is not None:
            for key, value in propriedades.items():
                self.__dict__[key] = value

    def __repr__(self):
        return "Lote:%r, terminal: %r, loteFin: %r, loteAut: %r, " \
               "arquivo: %r tipoTrans: %r" % (self.lote, self.terminal, self.lote_financeiro,
                                              self.lote_autorizador, self.arquivo, self.tipo_transacao)


class Icpt(RegistroVendaAdquirente):
    transacao_id = Column(Integer, ForeignKey('registro_venda_adquirente.id'))
    #pra fazer um pra um, mais so um lado sabe do outro e fazer a referencia para a proria tabela remote_side=[RegistroAdquirente.id],
    transacao = relationship('TransacaoAdquirente', uselist=False, remote_side=[RegistroVendaAdquirente.id])
    valor_intercambio = Column(DECIMAL)
    valor_taxa_bandeira = Column(DECIMAL)
    valor_intercambio = Column(DECIMAL)
    valor_margem = Column(DECIMAL)
    tipo_cartao = Column(Text)
    codigo_descricao = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'Icpt'
    }
    def __init__(self, propriedades=None):
        RegistroVendaAdquirente.__init__(self)
        self.lote = None
        self.valor_intercambio = None
        self.valor_taxa_bandeira = None
        self.valor_margem = None
        self.tipo_cartao = None
        self.codigo_descricao = None
        self.transacao = None

        if propriedades is not None:
            for key, value in propriedades.items():
                self.__dict__[key] = value

    def __repr__(self):
        return "Lote: %r, Val.Int: %r, Val.Tax: %r, Val.Mar: %r, nsu: %r, itrn: %r, tipoCartao: %r, codigoDes: %r, " \
               "trans: %r" % (self.lote, self.valor_intercambio, self.valor_taxa_bandeira, self.valor_margem, self.nsu,
                              self.itrn, self.tipo_cartao, self.codigo_descricao, self.transacao)