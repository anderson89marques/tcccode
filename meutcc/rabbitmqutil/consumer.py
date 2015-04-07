__author__ = 'anderson'
import pika
import time
import transaction
from meutcc.scripts.processador_arquivo import ProcessarArquivo
import logging
log = logging.getLogger(__name__)


class Consumer(object):
    def __init__(self):
        self.connection = None
        self.channel = None
        self.name = None
        #self.connect()

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.104'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='hello')
        self.channel.basic_consume(self.callback,
                                    queue='hello')

    def callback(self, ch, method, properties, body):
        print("Cosumer name: %r" % self.name)
        print("[*] Recebido: %r" % body)
        p = ProcessarArquivo()
        print("Aqui 3")
        #nomes_arquivos = glob("meutcc/arquivos_para_processar/*T*_171014.txt")
        #print(nomes_arquivos)
        #for nome_arquivo in nomes_arquivos:
        print("Aqui 5")
        time.sleep(10) #body.decode("utf8").count('.')
        with transaction.manager as trans:
            inicio = time.time()
            p.processar(body.decode("utf8"))
            print("TEMPO DE EXECUCAO %r" % (time.time() - inicio))
        print("[*] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        print("Esperando Mensagem! %r" % self.name)
        self.channel.start_consuming()






