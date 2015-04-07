__author__ = 'anderson'
"""
Este e responsavel por processar os arquivos de entrada, transformando os
dados contidos neles em objetos e armazenandos no banco de dados.

data inicial: 04/12/2014
data final: ?
"""

from datetime import datetime, date
import time
from glob import glob
from meutcc.banco.mocks import (TipoProcessamentoAdquirente,
                                TipoTransacao)
from meutcc.banco.Enums import TipoArquivo
import transaction
from meutcc.banco.models import (DBSession, ArquivoAdquirente, Icpt,
                                 LoteVendaAdquirente, LoteParceladoFuturoAdquirente, TransacaoAdquirente)
import inspect


format_data_hora = "%d%m%Y"
format_data = "%d%m%Y"


#ddMMyyyyHHmmss ainda nao esta sendo usado
def parse_data_hora(a, b):
    data = datetime.strptime(b, format_data_hora).date()
    print("parse_data_hora: %r" % data)
    return data


#ddMMyyyy
def parse_data(d):
    if d:
        data = datetime.strptime(d, format_data).date()
        print("parse_data: %r" % data)
        return data


def parse_tipo_transacao(x):
    return TipoTransacao.__getitem__(x).value


def parse_valor(s, v, d=2):
    if v:
        valor = long(v)/(10.0**2)
        if s == '-':
           valor = -valor
        return valor
    else:
        return 0.0


def parse_valor_total(c):
    tparc = c[14].strip()
    vTot = c[16].strip()
    val = parse_valor(c[17], c[18]) if tparc == "" and vTot == "" else parse_valor(c[15], c[16])
    return val


class ProcessarArquivo(object):
    def __init__(self):
        self.HEADER = '02'
        self.LOTE_VENDA = '06'
        self.TRANSACAO = '11'
        self.ICPT = '12'
        self.DADOS_ADICIONAIS = '15'
        self.LOTE_PARC_FUTURO = '20'
        self.TRAILLER = '98'
        self.SESSAO = DBSession
        #VAI REPRESENTAR O BANCO DE DADOS
        self.BANCO = []
        self.BANCOLOTEVENDA = []
        self.BANCOTRANSACAO = []
        self.BANCOICPT = []
        self.BANCOLOTEPARCELADO = []

        self.mapa = {'02': {'func': self.tratar_header,
                       0: {'campo': 'tipoRegistro', 'default': '02'},
                       1: {'campo': 'destinatario'},
                       2: {'campo': 'grupoClientes', 'ignorar': True},
                       3: {'campo': 'moeda', 'default': 'BRL'},
                       4: {'campo': 'adquirente', 'default': 'ELAVON'},
                       5: {'campo': 'extrato', 'default': 'EXTRATO ELETRONICO DE VENDAS'},
                       6: {'campo': 'data', 'ignorar': True},
                       7: {'campo': 'data_arquivo', 'parse': lambda x, y: parse_data_hora(x, y[6])},
                       8: {'campo': 'periodo_inicial', 'parse': parse_data},
                       9: {'campo': 'periodo_final', 'parse': parse_data},
                       10: {'campo': 'tipo_processamento'},
                       11: {'campo': 'data_processamento', 'parse': parse_data},
                       12: {'campo': 'versao'}},
                '06': {'func': self.tratar_lote_venda,
                       0: {'campo': 'tipo_registro', 'default': '06'},
                       1: {'campo': 'cnpj'},
                       2: {'campo': 'estabelecimento'},
                       3: {'campo': 'terminal'},
                       4: {'campo': 'lote_autorizador', 'parse': lambda x: long(x) if x else None},
                       5: {'campo': 'lote_financeiro', 'parse': lambda x: long(x) if x else None},
                       6: {'campo': 'data_processamento', 'parse': parse_data},
                       7: {'campo': 'data_pagamento_prevista', 'parse': parse_data},
                       8: {'campo': 'tipo_transacao', 'parse': parse_tipo_transacao},
                       9: {'campo': 'produto'},
                       10: {'campo': 'parcela', 'parse': lambda x: int(x) if x else 1},
                       11: {'campo': 'total_parcelas', 'parse': lambda x: int(x) if x else 1},
                       12: {'campo': 'sinal', 'ignorar': True},
                       13: {'campo': 'valor_bruto', 'parse': lambda v, s: parse_valor(s[12], v)},
                       14: {'campo': 'sinal', 'ignorar': True},
                       15: {'campo': 'valor_taxa_desconto', 'parse': lambda v, s: parse_valor(s[14], v)},
                       16: {'campo': 'sinal', 'ignorar': True},
                       17: {'campo': 'valor_liquido', 'parse': lambda v, s: parse_valor(s[16], v)},
                       18: {'campo': 'noItens', 'ignorar': True, 'parse': lambda x: int(x) if x else 0},
                       19: {'campo': 'descricao'}},
                '11': {'func': self.tratar_transacao,
                       0: {'campo': 'tipoRegistro', 'default': '11'},
                       1: {'campo': 'estabelecimeto'},
                       2: {'campo': 'terminal'},
                       3: {'campo': 'data', 'parse': parse_data},
                       4: {'campo': 'data_transacao', 'parse': lambda x, y: parse_data_hora(x, y[3])},
                       5: {'campo': 'lote_autoriador', 'parse': lambda x: long(x) if x else None},
                       6: {'campo': 'lote_financeiro', 'parse': lambda x: long(x) if x else None},
                       7: {'campo': 'cartao'},
                       8: {'campo': 'codigo_autorizacao'},
                       9: {'campo': 'nsu', 'parse': lambda x: long(x) if x else None},
                       10: {'campo': 'itrn', 'parse': lambda x: long(x) if x else None},
                       11: {'campo': 'modo_captura'},
                       12: {'campo': 'descricao'},
                       13: {'campo': 'parcela', 'parse': lambda x: int(x) if x else 1},
                       14: {'campo': 'total_parcela', 'parse': lambda x: int(x) if x else 1},
                       15: {'campo': 'sinal', 'ignorar': True},
                       16: {'campo': 'valor_total', 'parse': lambda v, s: parse_valor_total(s)},
                       17: {'campo': 'sinal', 'ignorar': True},
                       18: {'campo': 'valor_parcela', 'parse': lambda v, s: parse_valor(s[17], v)},
                       19: {'campo': 'sinal', 'ignorar': True},
                       20: {'campo': 'valor_taxa_desconto', 'parse': lambda v, s: parse_valor(s[19], v, 6)},
                       21: {'campo': 'sinal', 'ignorar': True},
                       22: {'campo': 'valor_liquido', 'parse': lambda v, s: parse_valor(s[21], v, 6)},
                       23: {'campo': 'taxa_desconto', 'parse': lambda v, s: parse_valor('', v, 6)},
                       24: {'campo': 'tarifa', 'parse': lambda v, s: parse_valor('', v, 6)}},
                '12': {'func': self.tratar_icpt,
                       0: {'campo': 'tipoRegistro', 'default': '12'},
                       1: {'campo': 'estabelecimeto'},
                       2: {'campo': 'itrn', 'parse': lambda x: long(x) if x else None},
                       3: {'campo': 'nsu', 'parse': lambda x: long(x) if x else None},
                       4: {'campo': 'tipo_cartao'},
                       5: {'campo': 'codigo_descricao', 'parse': lambda x: int(x) if x else 0},
                       6: {'campo': 'sinal', 'ignorar': True},
                       7: {'campo': 'valor_intercambio', 'parse': lambda v, s: parse_valor(s[6], v, 6)},
                       8: {'campo': 'sinal', 'ignorar': True},
                       9: {'campo': 'valor_taxa_bandeira', 'parse': lambda v, s: parse_valor(s[8], v, 6)},
                       10: {'campo': 'sinal', 'ignorar': True},
                       11: {'campo': 'valor_margem', 'parse': lambda v, s: parse_valor(s[10], v, 6)}},
                '15': {'func': self.tratar_dados_adicionais,
                       0: {'campo': 'tipoRegistro', 'default': '15'},
                       1: {'campo': 'estabelecimeto'},
                       2: {'campo': 'itrn', 'parse': lambda x: long(x) if x else None},
                       3: {'campo': 'nsu', 'parse': lambda x: long(x) if x else None},
                       4: {'campo': 'descricao'},
                       5: {'campo': 'transactionId'}},
                '20': {'func': self.tratar_lote_parcelado_futuro,
                       0: {'campo': 'tipoRegistro', 'default': '20'},
                       1: {'campo': 'cnpj'},
                       2: {'campo': 'estabelecimeto'},
                       3: {'campo': 'terminal'},
                       4: {'campo': 'lote_autoriador', 'parse': lambda x: long(x) if x else None},
                       5: {'campo': 'lote_financeiro', 'parse': lambda x: long(x) if x else None},
                       6: {'campo': 'data_processamento', 'parse': parse_data},
                       7: {'campo': 'data_pagamento_prevista', 'parse': parse_data},
                       8: {'campo': 'tipo_transacao', 'parse': parse_tipo_transacao},
                       9: {'campo': 'produto'},
                       10: {'campo': 'parcela', 'parse': lambda x: long(x) if x else None},
                       11: {'campo': 'total_parcela', 'parse': lambda x: long(x) if x else None},
                       12: {'campo': 'sinal', 'ignorar': True},
                       13: {'campo': 'valor_bruto', 'parse': lambda v, s: parse_valor(s[12], v)},
                       14: {'campo': 'sinal', 'ignorar': True},
                       15: {'campo': 'valor_taxa_desconto', 'parse': lambda v, s: parse_valor(s[14], v)},
                       16: {'campo': 'sinal', 'ignorar': True},
                       17: {'campo': 'valor_liquido', 'parse': lambda v, s: parse_valor(s[16], v)},
                       18: {'campo': 'noItens', 'ignorar': True, 'parse': lambda x: int(x) if x else 0},
                       19: {'campo': 'descricao'}},
                '98': {}
                }

    def tratar_header(self, obj):
        print("HEADER %r" % obj)
        if not obj.has_key('arquivo'):
            arquivo = ArquivoAdquirente()
            if obj.has_key('nome_arquivo'):
                arquivo.nome = obj.get('nome_arquivo')
                if arquivo.nome != None:
                    if arquivo.nome in self.BANCO: #vai fazer busca no Banco de dados
                        print("Arquivo %s ja processado")
                    else:
                        for campo, valor in obj.items():
                            arquivo[campo] = valor

                        if arquivo.destinatario != None:
                            arquivo.cadeia = arquivo.destinatario[5:]

                        arquivo.tipo = TipoArquivo.ARQUIVO_VENDA_ADQUIRENTE.value
                        print("Arquivo criado %s" % arquivo)
                        self.BANCO.append(arquivo.nome)
                        self.SESSAO.add(arquivo) #salvando no banco

                        obj['arquivo'] = arquivo
                        print("BANCO:%r:" % self.BANCO)
                        obj['status'] = "ok"
        else:
            raise RuntimeError("Arquivo ja procesado!")
        return obj


    def tratar_lote_venda(self, obj):
        print("LOTE VENDA %r" % obj)
        lt = self.findLoteVenda(obj) #Aqui so retorna false. Quando tiver a base de dados eh preciso buscar no banco
        if lt and obj['arquivo'] is not None and obj['arquivo'].tipoProcessamento == TipoProcessamentoAdquirente.SUBMISSAO:
            #fazer algo
            pass
        elif lt and obj['arquivo'] is not None and obj['arquivo'].tipoProcessamento == TipoProcessamentoAdquirente.REPROCESSAMENTO:
            #fazer algo
            pass
        elif not lt:
            lt = LoteVendaAdquirente(obj)
            print("LoteVenda Criado %s" % lt)
            self.SESSAO.add(lt) #salvando no banco
        obj['loteVenda'] = lt
        print("LOTE VENDA AQUI: %r" % (obj['loteVenda']))
        obj['status'] = "ok"
        return obj


    def tratar_transacao(self, obj):
        print("TRANSACAO %r" % obj)
        t = self.findTransacao(obj)
        if t and obj['arquivo'] is not None and obj['arquivo'].tipoProcessamento == TipoProcessamentoAdquirente.SUBMISSAO:
            #fazer algo
            pass
        elif t and obj['arquivo'] is not None and obj['arquivo'].tipoProcessamento == TipoProcessamentoAdquirente.REPROCESSAMENTO:
            #fazer algo
            pass
        elif not t:
            t = TransacaoAdquirente(obj)
            print("Transacao Adquirente Criada %s" % t)

        if obj['arquivo'] is not None:
            t.arquivo = obj['arquivo']

        if obj['loteVenda'] is not None:
            t.lote = obj['loteVenda']

        self.BANCOLOTEVENDA.append(t)
        self.SESSAO.add(t)

        obj['transacao'] = t
        obj['status'] = "ok"
        return obj


    def tratar_icpt(self, obj):
        print("ICPT %r" %obj)
        if obj['nsu'] is None:
            obj['nsu'] = long(0)

        i = self.findIcpt(obj)
        if i and obj['arquivo'] is not None and obj['arquivo'].tipoProcessamento == TipoProcessamentoAdquirente.SUBMISSAO:
            #fazer algo
            pass
        elif i and obj['arquivo'] is not None and obj['arquivo'].tipoProcessamento == TipoProcessamentoAdquirente.REPROCESSAMENTO:
            #fazer algo
            pass
        elif not i:
            i = Icpt(obj)
            print("ICPT Criado %s" % i)
            self.BANCOICPT.append(i)

            if obj['arquivo'] is not None:
                i.arquivo = obj['arquivo']

            if obj['loteVenda'] is not None:
                i.lote = obj['loteVenda']

            if obj['transacao'] and obj['transacao'].itrn == obj['itrn'] and obj['transacao'].nsu == obj['nsu']:
                print("ATRIBUINDO TRANSACAO")
                i.transacao = obj['transacao']
        self.BANCOICPT.append(i)
        self.SESSAO.add(i)
        obj['status'] = "ok"
        return obj


    def tratar_lote_parcelado_futuro(self, obj):
        print("LOTE PARCELADO FUTURO %r" % obj)
        lpv = self.findLoteParceladoFuturo(obj) #Aqui so retorna false. Quando tiver a base de dados eh preciso buscar no banco
        if lpv and obj['arquivo'] is not None and obj['arquivo'].tipoProcessamento == TipoProcessamentoAdquirente.SUBMISSAO:
            #fazer algo
            pass
        elif lpv and obj['arquivo'] is not None and obj['arquivo'].tipoProcessamento == TipoProcessamentoAdquirente.REPROCESSAMENTO:
            #fazer algo
            pass
        elif not lpv:
            lpv = LoteParceladoFuturoAdquirente(obj)
            print(">>>> TYPEEEE Lote :%r : %r" % (type(lpv.loteVenda), type(obj['loteVenda'])))
            lpv.lote_venda = obj['loteVenda']
            #lpv.arquivo = obj['arquivo']
            print("LoteParcelado Criado %s" % lpv)
            self.BANCOLOTEPARCELADO.append(lpv)
            self.SESSAO.add(lpv)
        obj['status'] = "ok"
        return obj


    def tratar_dados_adicionais(self, obj):
        return obj


    def processa_tokens(self, nome_arquivo, tokens, contexto):
        pre_obj = {'nome_arquivo': nome_arquivo}
        print("tokens ::::::::: %r" % tokens[0])
        pre_obj['reg'] = tokens[0]
        pre_obj.update(contexto)
        print("contexto: %r" % pre_obj)
        mapa_campos = self.mapa.get(tokens[0])
        for key, campos in mapa_campos.items():
            if key == 'func' or campos.get('ignorar'):
                continue

            print("key:%s, campos: %r, token[key]:%r" %(key, campos, tokens[key]))
            if campos.has_key('default') and campos.get('default') != tokens[key]:
                raise RuntimeError("Erro ao validar dado!")

            val = tokens[key]
            if campos.has_key('parse'):
                if len(inspect.getargspec(campos.get('parse')).args) == 1: #numero de argumentos da funcao
                    val = campos.get('parse')(val)
                else:
                    val = campos.get('parse')(val, tokens)
            pre_obj[campos.get('campo')] = val
        func = mapa_campos.get('func')
        if func:
            func(pre_obj) #chamando a funcao que vai tratar os dados.
        return pre_obj

    def processar(self, nome_arquivo, tras=None):
        print("processando arquivo %s" %(nome_arquivo))
        contextoInicial = {}
        erros = {}
        with open(nome_arquivo) as p:
            cont = 0
            for linha in p.readlines():
                cont += 1
                contexto = {}
                contexto.update(contextoInicial)
                tokens = linha.strip().split("|")
                print("linha: %r" % linha)
                r = self.processa_tokens(nome_arquivo, tokens, contexto)
                print("RESPOSTA: %r" % r)
                if r['reg'] == '02' and r['arquivo'] is not None:
                    print("02")
                    contextoInicial['arquivo'] = r['arquivo']
                elif r['reg'] == self.LOTE_VENDA and r['loteVenda'] is not None:
                    print("06")
                    contextoInicial['loteVenda'] = r['loteVenda']
                    print("CONTEXTO INICIAL AQUI%r" %(contextoInicial['loteVenda']))
                elif r['reg'] == self.LOTE_PARC_FUTURO:
                    print("20")
                    #break
                elif r['reg'] == self.TRANSACAO and r['transacao'] is not None:
                    print("11")
                    contextoInicial['transacao'] = r['transacao']
                #if cont == 100:
                    #tras.commit()
                    #self.SESSAO.commit()
                    #nt = 0

                if r.has_key('status') and r['status'] != 'ok':
                    erros = {'linha': linha}
        if erros.has_key('linha'):
            print("Resultado do processamento: Erro na linha %r" % erros['linha'])
        else:
            print("Resultado do processamento: Processamento Realizado com sucesso! :D")

    def findLoteVenda(self, ctx):
        return False

    def findLoteParceladoFuturo(self, ctx):
        return False

    def findTransacao(self, ctx):
        return False

    def findIcpt(self, ctx):
        return False


if __name__ == '__main__':
    with transaction.manager:
        inicio = time.time()
        p = ProcessarArquivo()
        nomes_arquivos = glob("../arquivos_para_processar/*T*_171014.txt")
        for nome_arquivo in nomes_arquivos:
            p.processar(nome_arquivo)
        print("TEMPO DE EXECUCAO %r" % (time.time() - inicio))
