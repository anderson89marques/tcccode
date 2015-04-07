__author__ = 'anderson'
import pika
import sys
from glob import glob
import logging
log = logging.getLogger(__name__)


class Producer(object):
    def __init__(self):
        self.connection = None
        self.channel = None
        self.message = "Hello world........."

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.104'))
        self.channel = self.connection.channel()
        #definindo a fila
        self.channel.queue_declare(queue='hello')

    def enviar_msg(self):
        #colocando em uma lista o nome de todos os arquivos
        nomes_arquivos = glob("meutcc/arquivos_para_processar/*T*.txt")
        for nome_arquivo in nomes_arquivos:
            self.channel.basic_publish(exchange='',
                                   routing_key='hello',
                                   body=nome_arquivo)
        self.connection.close()
        print("[X] Mensagem %r enviado!" % self.message)