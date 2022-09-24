# V3
import os
import base64
from threading import Thread

import requests
from flask import Flask, request
from events.thread_emitter import ThreadEmitter
from constants import secrets


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
        app = Flask(__name__)

        @app.route("/spotify", methods=['GET'])
        def OnSpotifyAuth():
            args = request.args
            code = args.get('code')
            url = "https://accounts.spotify.com/api/token"

            payload = {
                "code" : code,
                "redirect_uri":  secrets['spotify']['redirect_uri'],
                'grant_type': "authorization_code"
            }

            auth_code = secrets['spotify']['client_id'] + ':' + secrets['spotify']['client_secret']
            headers = {"Authorization": "Basic " + base64.urlsafe_b64encode((auth_code).encode('ascii')).decode('ascii'),
                       'Content-Type': 'application/x-www-form-urlencoded'}
            auth_data = requests.post(url=url, headers=headers, data=payload).json()
            if len(self.spotify_callbacks) > 0:
                for callback in self.spotify_callbacks:
                    callback(auth_data)
            return "<p>Done</p>"

        server_job_processor = Thread(target=self.ProcessJobThreadFunc,daemon=True,group=None)
        server_job_processor.start()
        app.run(host='0.0.0.0', port=24559, debug=False)

server = ServerThread()
server.start()
