import json
import webbrowser

import requests

from events import global_emitter
from skills import RegisterSkill, skill
from constants import secrets
from urllib.parse import urlencode
from threads.server import server
from os import path, getcwd

SPOTIFY_AUTH_PATH = path.join(getcwd(), 'spotify_auth.json')

spotify_auth = None
header_data = None


def UpdateHeader(auth):
    global header_data
    header_data = {
        "Authorization": "{} {}".format(auth['token_type'], auth['access_token']),
        'Content-Type': 'application/json',
    }


def OnSpotifyAuthReceived(auth):
    global spotify_auth
    spotify_auth = auth
    UpdateHeader(auth)
    with open(SPOTIFY_AUTH_PATH, "w") as outfile:
        json.dump(spotify_auth, outfile, indent=4)


if not spotify_auth:
    if not path.exists(SPOTIFY_AUTH_PATH):
        authorize_url = "https://accounts.spotify.com/authorize?response_type=code&" + urlencode(
            {'client_id': secrets['spotify']['client_id'], 'scope': secrets['spotify']['scope'],
             'redirect_uri': secrets['spotify']['redirect_uri']})
        new = 2  # not really necessary, may be default on most modern browsers
        server.AddJob('add_spotify_callback', OnSpotifyAuthReceived)
        webbrowser.open(authorize_url, new=new)
    else:
        with open(SPOTIFY_AUTH_PATH, "r") as infile:
            spotify_auth = json.load(infile)
            UpdateHeader(spotify_auth)


@skill(r"^pause music$")
def Pause(phrase, match):
    requests.put(url="https://api.spotify.com/v1/me/player/pause", headers=header_data).content


@skill(r"^resume music$")
def Resume(phrase, match):
    requests.put(url="https://api.spotify.com/v1/me/player/play", headers=header_data)


@skill(r"^skip music$")
def Skip(phrase, match):
    requests.post(url="https://api.spotify.com/v1/me/player/next", headers=header_data)


@skill(r"^(play)[\s]+(track|playlist|album)[\s]+(.+)")
def Play(phrase, match):
    print(match)
    result = requests.get(url="https://api.spotify.com/v1/search", headers=header_data, params={
        "q": match[0][2],
        "type": [match[0][1]]
    }).json()

    query = '{}s'.format(match[0][1])
    print(result[query]['items'][0]['uri'])
    if result[query] and len(result[query]['items']) > 0:
        if match[0][1] == 'track':
            requests.put(url="https://api.spotify.com/v1/me/player/play", headers=header_data, json={
                'uris': [result[query]['items'][0]['uri']]
            })
        else:

            requests.put(url="https://api.spotify.com/v1/me/player/play", headers=header_data, json={
                'context_uri': result[query]['items'][0]['uri'],
                'offset' : { 'position' : 0}
            })

        global_emitter.emit('say',"Playing {}".format(result[query]['items'][0]['name']),True)

@skill(r"^(add)[\s]+(.+)")
def Play(phrase, match):
    result = requests.get(url="https://api.spotify.com/v1/search", headers=header_data, params={
        "q": match[0][1],
        "type": ['track']
    }).json()

    if result['tracks'] and len(result['tracks']['items']) > 0:

        print(requests.post(url="https://api.spotify.com/v1/me/player/queue?uri={}".format(result['tracks']['items'][0]['uri']), headers=header_data).content)
        global_emitter.emit('say',"Queued {}".format(result['tracks']['items'][0]['name']),True)
