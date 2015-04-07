from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError

from .banco.models import DBSession, LoteVendaAdquirente, LoteParceladoFuturoAdquirente, TransacaoAdquirente, Icpt

import transaction
import time
from .rabbitmqutil.producer import Producer
from .rabbitmqutil.consumer import Consumer
import logging
log = logging.getLogger(__name__)


class TccViwes():
    def __init__(self, request):
        self.request = request

    @view_config(route_name='startconsume', renderer='json')
    def start_consume(self):
        print("No start Consume")
        print(self.request.params)
        with transaction.manager as trans:
            c = Consumer()
            c.name = "CONSUMER 1"
            c.connect()
            c.start_consuming()
        return {"nome": "Anderson"}

    @view_config(route_name='processa', renderer='templates/main.jinja2')
    def minha_view(self):
        print("Aqui")
        #with transaction.manager as trans:
        print("Iniciando o producer!")
        prod = Producer()
        prod.connect()
        prod.enviar_msg()
        print("Aqui 2")
        return {'anjo': "Tempo execucao"}

    @view_config(route_name='home', renderer='templates/home.jinja2')
    def home(self):
        return {"nome": "Anderson"}

    @view_config(route_name='lote_venda', renderer='templates/lotesVendas.jinja2')
    def lotes_vendas(self):
        print("Lote Venda")
        with transaction.manager:
            l = DBSession.query(LoteVendaAdquirente).all()
        return {"lista": l}

    @view_config(route_name='lote_parcelado', renderer='templates/lotesParcelados.jinja2')
    def lotes_parcelados(self):
        print("Lote Parcelado Futuro")
        with transaction.manager:
            l = DBSession.query(LoteParceladoFuturoAdquirente).all()
        return {"lista": l}

    @view_config(route_name='transacao', renderer='templates/transacao.jinja2')
    def transacoes(self):
        print("Transacao")
        print(self.request.params)
        with transaction.manager:
            l = DBSession.query(TransacaoAdquirente).all()
            print(l[0].nsu)
        return {"lista": l[:12]}

    @view_config(route_name='icpt', renderer='templates/icpt.jinja2')
    def icpts(self):
        print("ICPT")
        with transaction.manager:
            l = DBSession.query(Icpt).all()
        return {"lista": l[:12]}

    conn_err_msg = """\
    Pyramid is having a problem using your SQL database.  The problem
    might be caused by one of the following things:

    1.  You may need to run the "initialize_meutcc_db" script
        to initialize your database tables.  Check your virtual
        environment's "bin" directory for this script and try to run it.

    2.  Your database server may not be running.  Check that the
        database server referred to by the "sqlalchemy.url" setting in
        your "development.ini" file is running.

    After you fix the problem, please restart the Pyramid application to
    try it again.
    """

