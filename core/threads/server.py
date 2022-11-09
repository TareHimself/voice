# V3
import asyncio
import base64
from subprocess import Popen
import sys
from threading import Thread
import aiohttp
import tornado.web
from core.events import ThreadEmitter
from uuid import uuid4
# Third-party library
from aiohttp import web
from core.logger import log
from core.singletons import GetSingleton, Singleton
from core.threads.timer import StartTimer
from core.events import gEmitter
from core.constants import SINGLETON_SERVER_ID


def CreateProxiedBody(body):
    return web.json_response({"body": body})


# class WebServer():
#     def __init__(self):
#         self.app = web.Application()

#     def Get(self, path: str):
#         def inner(func):
#             self.app.router.add_get(path, func)
#             return func

#         return inner

#     def Post(self, path: str):
#         def inner(func):
#             self.app.router.add_post(path, func)
#             return func

#         return inner

#     def Put(self, path: str):
#         def inner(func):
#             self.app.router.add_put(path, func)
#             return func

#         return inner

#     def Delete(self, path: str):
#         def inner(func):
#             self.app.router.add_delete(path, func)
#             return func

#         return inner

#     def Delete(self, path: str):
#         def inner(func):
#             self.app.router.add_delete(path, func)
#             return func

#         return inner

#     def listen(self, host: str, port: int):
#         web.run_app(self.app, host=host, port=port, handle_signals=False)


# class ServerThread(ThreadEmitter):

#     def __init__(self):
#         super().__init__()
#         self.spotify_callbacks = []
#         self.WebServer = None

#     def HandleJob(self, job: str, *args, **kwargs):
#         log(job)
#         if job == 'end':
#             asyncio.run(self.WebServer.app.shutdown())
#             asyncio.run(self.WebServer.app.cleanup())
#         elif job == 'add_spotify_callback':
#             self.spotify_callbacks.append(args[0])

#     def ProcessJobThreadFunc(self):
#         while True:
#             self.ProcessJobs()

#     def run(self):
#         self.WebServer = WebServer()

#         @self.WebServer.Get("/spotify")
#         @self.WebServer.Post("/telegram/webhook")
#         async def OnTelegramUpdate(request: web.Request):

#             return web.json_response({"status": 200})

#         @self.WebServer.Get("/telegram/webhook")
#         async def OnTelegramGet(request: web.Request):

#             return web.json_response({"status": 200})

#         @self.WebServer.Get("/")
#         async def OnHome(request: web.Request):

#             return CreateProxiedBody("THIS IS A VOICE ASSISTANT BOI")

#         server_job_processor = Thread(
#             target=self.ProcessJobThreadFunc, daemon=True, group=None)
#         server_job_processor.start()
#         self.WebServer.listen('localhost', 24559)


def _start_proxy():
    proxy_process = Popen(['npm', 'start'], stdout=sys.stdout,
                          stderr=sys.stderr, shell=True)

    def end_process(sig, frame):
        #Popen("TASKKILL /F /PID {pid} /T".format(pid=proxy_process.pid))
        proxy_process.terminate()

    gEmitter.on('terminate', end_process)

    proxy_process.communicate()


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
    server_singleton: ServerSingleton = GetSingleton(SINGLETON_SERVER_ID)


def StartServer():
    ServerSingleton()
