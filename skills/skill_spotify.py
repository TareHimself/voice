import base64
import datetime
import json
import webbrowser
import requests
from word2number import w2n
from num2words import num2words
from skills import Skill
from constants import secrets
from urllib.parse import urlencode
from threads.server import server
from os import path, getcwd

from utils import DisplayUiMessage, TextToSpeech, EndCommand

SPOTIFY_AUTH_PATH = path.join(getcwd(), 'spotify_auth.json')

spotify_auth = None
header_data = None
spotify_auth_refresh = None


def UpdateHeader(auth):
    global header_data
    header_data = {
        "Authorization": "{} {}".format(auth['token_type'], auth['access_token']),
        'Content-Type': 'application/json',
    }


def OnSpotifyAuthReceived(auth):
    global spotify_auth
    global spotify_auth_refresh
    spotify_auth = auth
    spotify_auth_refresh = datetime.datetime.utcnow() + datetime.timedelta(seconds=spotify_auth['expires_in'])
    spotify_auth['expires_at'] = spotify_auth_refresh.isoformat()
    del spotify_auth['expires_in']
    UpdateHeader(auth)
    with open(SPOTIFY_AUTH_PATH, "w") as outfile:
        json.dump(spotify_auth, outfile, indent=4)


def ValidateSpotifyAuth():
    global spotify_auth
    global spotify_auth_refresh

    if not spotify_auth_refresh:
        return False

    if spotify_auth_refresh < datetime.datetime.utcnow():
        payload = {
            'grant_type' : 'refresh_token',
            "refresh_token" : spotify_auth['refresh_token'],
            "client_id" : secrets['spotify']['client_id']
        }

        auth_code = secrets['spotify']['client_id'] + ':' + secrets['spotify']['client_secret']
        headers = {"Authorization": "Basic " + base64.urlsafe_b64encode(auth_code.encode('ascii')).decode('ascii'),
                   'Content-Type': 'application/x-www-form-urlencoded'}
        url = "https://accounts.spotify.com/api/token"
        auth_data = requests.post(url=url, headers=headers, data=payload).json()
        print(auth_data)
        spotify_auth_refresh = datetime.datetime.utcnow() + datetime.timedelta(seconds=auth_data['expires_in'])
        spotify_auth['access_token'] = auth_data['access_token']
        spotify_auth['expires_at'] = spotify_auth_refresh.isoformat()
        UpdateHeader(spotify_auth)
        with open(SPOTIFY_AUTH_PATH, "w") as outfile:
            json.dump(spotify_auth, outfile, indent=4)

    return True


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
            spotify_auth_refresh = datetime.datetime.fromisoformat(spotify_auth['expires_at'])
            ValidateSpotifyAuth()
            UpdateHeader(spotify_auth)


def SpotifySkillValidation(f):
    def inner(*args, **kwargs):
        if ValidateSpotifyAuth():
            f(*args, **kwargs)
        return

    return inner


@Skill("skill_spotify_pause")
@SpotifySkillValidation
def Pause(phrase, keywords):
    requests.put(url="https://api.spotify.com/v1/me/player/pause", headers=header_data)
    EndCommand()


@Skill("skill_spotify_resume")
@SpotifySkillValidation
def Resume(phrase, keywords):
    requests.put(url="https://api.spotify.com/v1/me/player/play", headers=header_data)
    EndCommand()


@Skill("skill_spotify_skip")
@SpotifySkillValidation
def Skip(phrase, keywords):
    requests.post(url="https://api.spotify.com/v1/me/player/next", headers=header_data)
    EndCommand()


@Skill("skill_spotify_play","skill_music_play_specific")
@SpotifySkillValidation
def Play(phrase, keywords):
    print(keywords)
    keywords[0] = keywords[0].strip()

    if len(keywords[0]) == 0:
        keywords[0] = 'track'

    print(keywords)
    result = requests.get(url="https://api.spotify.com/v1/search", headers=header_data, params={
        "q": keywords[1],
        "type": [keywords[0]]
    }).json()

    query = '{}s'.format(keywords[0])
    if result[query] and len(result[query]['items']) > 0:
        if keywords[0] == 'track':
            print(requests.put(url="https://api.spotify.com/v1/me/player/play", headers=header_data, json={
                'uris': [result[query]['items'][0]['uri']]
            }).content)
        else:

            requests.put(url="https://api.spotify.com/v1/me/player/play", headers=header_data, json={
                'context_uri': result[query]['items'][0]['uri'],
                'offset': {'position': 0}
            })

        DisplayUiMessage("Playing {}".format(result[query]['items'][0]['name']))
    EndCommand()


@Skill("skill_spotify_add")
@SpotifySkillValidation
def AddToQueue(phrase, keywords):

    result = requests.get(url="https://api.spotify.com/v1/search", headers=header_data, params={
        "q": keywords[0],
        "type": ['track']
    }).json()

    if result['tracks'] and len(result['tracks']['items']) > 0:
        requests.post(
            url="https://api.spotify.com/v1/me/player/queue?uri={}".format(result['tracks']['items'][0]['uri']),
            headers=header_data)
        DisplayUiMessage("Queued {}".format(result['tracks']['items'][0]['name']))
    EndCommand()


@Skill("skill_spotify_volume")
@SpotifySkillValidation
def ModifyVolume(phrase, keywords):
    try:
        print(keywords)
        volume = int(w2n.word_to_num(keywords[0].strip()))

        if volume < 0 or volume > 100:
            raise Exception('Volume must be a number between 0 and 100 inclusive')

        requests.put(
            url="https://api.spotify.com/v1/me/player/volume?volume_percent={}".format(volume),
            headers=header_data)
        TextToSpeech('Set music volume to {}, Percent.'.format(num2words(volume)))
    except Exception as e:
        print(e)
        pass
    EndCommand()
