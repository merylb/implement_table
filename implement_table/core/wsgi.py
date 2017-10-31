"""
WSGI config for billingapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

import gevent
from django.core.wsgi import get_wsgi_application
from gevent import pywsgi
from ws4py.server.geventserver import WSGIServer

from ws4py.server.wsgiutils import WebSocketWSGIApplication

from implement_table.core.settings import DJANGO_HOST,   WEBSOCKET_HOST
from implement_table.ws.websocket import MnWebSocket

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "implement_table.core.settings")

http_server = pywsgi.WSGIServer(DJANGO_HOST, get_wsgi_application())


ws_server = WSGIServer(WEBSOCKET_HOST, WebSocketWSGIApplication(handler_cls=MnWebSocket))

g = [
    gevent.spawn(http_server.serve_forever),
    gevent.spawn(ws_server.serve_forever),
    # scheduler.start()
]

gevent.joinall(g, raise_error=True)

application = get_wsgi_application()
