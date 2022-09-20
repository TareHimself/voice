# V3
import os
from flask import Flask
from events.thread_emitter import ThreadEmitter

class ServerThread(ThreadEmitter):

    def __init__(self):
        super(ServerThread, self).__init__()

    def HandleJob(self, job: str, *args, **kwargs):
        pass

    def run(self):
        app = Flask(__name__)

        @app.route("/sp_auth")
        def OnSpotifyAuth():
            return "<p>Auth Here In the Future!</p>"

        app.run(host='0.0.0.0', port=5000, debug=False)
        while True:
            self.ProcessJobs()



def StartServer():
    server = StartServer()
    server.start()
    return
