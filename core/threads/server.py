# V3
import base64
from threading import Thread

import aiohttp
from core.events import ThreadEmitter
from core.constants import config
# Built-in library
import json
from uuid import uuid4
# Third-party library
from aiohttp import web



class WebServer:
	def __init__(self):
		self.app = web.Application()
		
	
	def Get(self,path:str):
		def inner(func):
			self.app.router.add_get(path,func)
			return func
		return inner

	def Post(self,path:str):
		def inner(func):
			self.app.router.add_post(path,func)
			return func
		return inner

	def Put(self,path:str):
		def inner(func):
			self.app.router.add_put(path,func)
			return func
		return inner

	def Delete(self,path:str):
		def inner(func):
			self.app.router.add_delete(path,func)
			return func
		return inner

	def Delete(self,path:str):
		def inner(func):
			self.app.router.add_delete(path,func)
			return func
		return inner

	def listen(self,host:str,port:int):
		web.run_app(self.app, host=host, port=port)

class ServerThread(ThreadEmitter):

    def __init__(self):
        super(ServerThread, self).__init__()
        self.spotify_callbacks = []

    def HandleJob(self, job: str, *args, **kwargs):
        print(job)
        if job == 'add_spotify_callback':
            self.spotify_callbacks.append(args[0])

    def ProcessJobThreadFunc(self):
        while True:
            self.ProcessJobs()
    def run(self):
        app = WebServer()

        @app.Get("/spotify")
        async def OnSpotifyAuth(request: web.Request):
            code = request.rel_url.query['code']
            url = "https://accounts.spotify.com/api/token"

            payload = {
                "code" : code,
                "redirect_uri":  config['spotify']['redirect_uri'],
                'grant_type': "authorization_code"
            }

            auth_code = config['spotify']['client_id'] + ':' + config['spotify']['client_secret']
            headers = {"Authorization": "Basic " + base64.urlsafe_b64encode((auth_code).encode('ascii')).decode('ascii'),
                       'Content-Type': 'application/x-www-form-urlencoded'}

            async with aiohttp.ClientSession() as session:
                async with session.post(url=url,headers=headers,data=payload) as resp:
                    auth_data = await resp.json()
                    if len(self.spotify_callbacks) > 0:
                        for callback in self.spotify_callbacks:
                            callback(auth_data)

            return web.Response(text="Done")

        server_job_processor = Thread(target=self.ProcessJobThreadFunc,daemon=True,group=None)
        server_job_processor.start()
        app.listen('localhost',24559)

server = ServerThread()
server.start()
