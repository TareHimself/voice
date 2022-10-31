# V3
import asyncio
import base64
from subprocess import Popen
import sys
from threading import Thread
import aiohttp
from core.events import ThreadEmitter
from core.constants import config
from uuid import uuid4
# Third-party library
from aiohttp import web

from core.singletons import GetSingleton, Singleton
from core.threads.timer import StartTimer
from core.events import gEmitter


def CreateProxiedBody(body):
    return web.json_response({"body": body})


class WebServer():
    def __init__(self):
        self.app = web.Application()

    def Get(self, path: str):
        def inner(func):
            self.app.router.add_get(path, func)
            return func

        return inner

    def Post(self, path: str):
        def inner(func):
            self.app.router.add_post(path, func)
            return func

        return inner

    def Put(self, path: str):
        def inner(func):
            self.app.router.add_put(path, func)
            return func

        return inner

    def Delete(self, path: str):
        def inner(func):
            self.app.router.add_delete(path, func)
            return func

        return inner

    def Delete(self, path: str):
        def inner(func):
            self.app.router.add_delete(path, func)
            return func

        return inner

    def listen(self, host: str, port: int):
        web.run_app(self.app, host=host, port=port, handle_signals=False)


class ServerThread(ThreadEmitter):

    def __init__(self):
        super().__init__()
        self.spotify_callbacks = []
        self.WebServer = None

    def HandleJob(self, job: str, *args, **kwargs):
        self.print(job)
        if job == 'end':
            asyncio.run(self.WebServer.app.shutdown())
            asyncio.run(self.WebServer.app.cleanup())
            print('STOPPED SERVER')
        elif job == 'add_spotify_callback':
            self.spotify_callbacks.append(args[0])

    def ProcessJobThreadFunc(self):
        while True:
            self.ProcessJobs()

    def run(self):
        self.WebServer = WebServer()

        @self.WebServer.Get("/spotify")
        async def OnSpotifyAuth(request: web.Request):
            code = request.rel_url.query['code']
            url = "https://accounts.spotify.com/api/token"

            payload = {
                "code": code,
                "redirect_uri": config['spotify']['redirect_uri'],
                'grant_type': "authorization_code"
            }

            auth_code = config['spotify']['client_id'] + \
                ':' + config['spotify']['client_secret']
            headers = {
                "Authorization": "Basic " + base64.urlsafe_b64encode((auth_code).encode('ascii')).decode('ascii'),
                'Content-Type': 'application/x-www-form-urlencoded'}

            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, data=payload) as resp:
                    auth_data = await resp.json()
                    if len(self.spotify_callbacks) > 0:
                        for callback in self.spotify_callbacks:
                            callback(auth_data)

            return CreateProxiedBody("Done")

        @self.WebServer.Post("/telegram/webhook")
        async def OnTelegramUpdate(request: web.Request):

            return web.json_response({"status": 200})

        @self.WebServer.Get("/telegram/webhook")
        async def OnTelegramGet(request: web.Request):

            return web.json_response({"status": 200})

        @self.WebServer.Get("/")
        async def OnHome(request: web.Request):

            return CreateProxiedBody("THIS IS A VOICE ASSISTANT BOI")

        server_job_processor = Thread(
            target=self.ProcessJobThreadFunc, daemon=True, group=None)
        server_job_processor.start()
        self.WebServer.listen('localhost', 24559)


def _start_proxy():
    proxy_process = Popen(['npm', 'start'], stdout=sys.stdout,
                          stderr=sys.stderr, shell=True)

    def end_process(sig, frame):
        #Popen("TASKKILL /F /PID {pid} /T".format(pid=proxy_process.pid))
        proxy_process.terminate()

    gEmitter.on('terminate', end_process)

    proxy_process.communicate()


def RunProxy():
    Thread(daemon=True, target=_start_proxy, group=None).start()


class ServerSingleton(Singleton):
    def __init__(self):
        super().__init__(id="server")
        self.server = ServerThread()
        self.server.start()
        RunProxy()


def OnStopServer():
    server_singleton: ServerSingleton = GetSingleton('server')


def StartServer():
    ServerSingleton()
