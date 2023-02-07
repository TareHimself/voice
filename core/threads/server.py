import asyncio
from subprocess import Popen, PIPE, STDOUT
import sys
from threading import Thread
import tornado.web
from aiohttp import web
from core.logger import log
from core.singletons import get_singleton, Singleton
from sys import platform
from core.events import GLOBAL_EMITTER
from core.constants import SINGLETON_SERVER_ID
from threading import Timer

a = Timer(0.1, lambda a: print(a))
a.cancel()


def CreateProxiedBody(body):
    return web.json_response({"body": body})


def _start_proxy():
    proxy_process = Popen(['npm', 'start'] if platform == 'win32' else ['npm start'], stdout=PIPE,
                          stderr=STDOUT, shell=True)

    def end_process(sig, frame):
        proxy_process.terminate()

    GLOBAL_EMITTER.on('terminate', end_process)

    while proxy_process.poll() is None:
        for line in iter(proxy_process.stdout.readline, b''):
            cur_line = line.decode('utf-8').strip()
            if len(cur_line) > 0:
                log(cur_line, logger_id="proxy")


def _RunProxy():
    Thread(daemon=True, target=_start_proxy, group=None).start()


class BaseRouteHandler(tornado.web.RequestHandler):
    async def get(self):
        self.write("Hello, world")


server_app = tornado.web.Application([
    (r"/", BaseRouteHandler),
], debug=True)


async def _start_server():
    global server_app
    server_app.listen(24559)
    await asyncio.Event().wait()


def _RunApp():
    Thread(daemon=True, target=lambda: asyncio.run(
        _start_server()), group=None).start()


class ServerSingleton(Singleton):
    def __init__(self):
        super().__init__(id=SINGLETON_SERVER_ID)
        _RunApp()
        self.app = server_app
        _RunProxy()


def OnStopServer():
    server_singleton: ServerSingleton = get_singleton(SINGLETON_SERVER_ID)


def StartServer():
    ServerSingleton()
