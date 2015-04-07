from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from banco.models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('processa', 'processa')
    config.add_route('lote_venda', 'lotevenda')
    config.add_route('lote_parcelado', 'lotesparcelados')
    config.add_route('transacao', 'transacaoes')
    config.add_route('icpt', 'icpts')
    config.add_route('startconsume', '/startconsume')
    config.scan()
    return config.make_wsgi_app()



### SIMPLE STARTUP
"""if __name__ == '__main__':
    settings = {
        'mako.directories': '%s:templates' % __name__,
    }
    app = main({}, **settings)
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 5000, app)
    server.serve_forever()
"""