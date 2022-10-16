import base64
from datetime import datetime,timedelta
import json
import webbrowser
import requests
from word2number import w2n
from num2words import num2words
from core.skills import Skill
from core.constants import config, DATA_PATH
from urllib.parse import urlencode
from core.threads import server
from os import path

from core.utils import DisplayUiMessage, TextToSpeech

SPOTIFY_AUTH_PATH = path.join(DATA_PATH, 'spotify_auth.json')

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
    if 'expires_in' in auth.keys(): 
        global spotify_auth
        global spotify_auth_refresh
        spotify_auth = auth
        spotify_auth_refresh = datetime.utcnow() + timedelta(seconds=spotify_auth['expires_in'])
        spotify_auth['expires_at'] = spotify_auth_refresh.isoformat()
        del spotify_auth['expires_in']
        UpdateHeader(auth)
        with open(SPOTIFY_AUTH_PATH, "w") as outfile:
            json.dump(spotify_auth, outfile, indent=4)


def ValidateSpotifyAuth():
    global spotify_auth
    global spotify_auth_refresh
    if not spotify_auth_refresh or 'spotify' not in config.keys():
        return False
    
    utc_now = datetime.utcnow()
    if spotify_auth_refresh < utc_now:
        payload = {
            'grant_type': 'refresh_token',
            "refresh_token": spotify_auth['refresh_token'],
            "client_id": config['spotify']['client_id']
        }

        auth_code = config['spotify']['client_id'] + ':' + config['spotify']['client_secret']
        headers = {"Authorization": "Basic " + base64.urlsafe_b64encode(auth_code.encode('ascii')).decode('ascii'),
                   'Content-Type': 'application/x-www-form-urlencoded'}
        url = "https://accounts.spotify.com/api/token"
        auth_data = requests.post(url=url, headers=headers, data=payload).json()
        spotify_auth_refresh = utc_now + timedelta(seconds=auth_data['expires_in'])
        spotify_auth['access_token'] = auth_data['access_token']
        spotify_auth['expires_at'] = spotify_auth_refresh.isoformat()
        UpdateHeader(spotify_auth)
        with open(SPOTIFY_AUTH_PATH, "w") as outfile:
            json.dump(spotify_auth, outfile, indent=4)

    return True


if not spotify_auth:
    if not path.exists(SPOTIFY_AUTH_PATH):
        authorize_url = "https://accounts.spotify.com/authorize?response_type=code&" + urlencode(
            {'client_id': config['spotify']['client_id'], 'scope': config['spotify']['scope'],
             'redirect_uri': config['spotify']['redirect_uri']})
        new = 2  # not really necessary, may be default on most modern browsers
        server.AddJob('add_spotify_callback', OnSpotifyAuthReceived)
        webbrowser.open(authorize_url, new=new)
    else:
        with open(SPOTIFY_AUTH_PATH, "r") as infile:
            spotify_auth = json.load(infile)
            spotify_auth_refresh = datetime.fromisoformat(spotify_auth['expires_at'])
            ValidateSpotifyAuth()
            UpdateHeader(spotify_auth)


def SpotifySkillValidation(f):
    async def inner(*args, **kwargs):
        if ValidateSpotifyAuth():
            await f(*args, **kwargs)
        return

    return inner


@Skill(["skill_spotify_pause"])
@SpotifySkillValidation
async def Pause(phrase, args):
    requests.put(url="https://api.spotify.com/v1/me/player/pause", headers=header_data)


@Skill(["skill_spotify_resume"])
@SpotifySkillValidation
async def Resume(phrase, args):
    requests.put(url="https://api.spotify.com/v1/me/player/play", headers=header_data)


@Skill(["skill_spotify_skip"])
@SpotifySkillValidation
async def Skip(phrase, args):
    requests.post(url="https://api.spotify.com/v1/me/player/next", headers=header_data)


@Skill(["skill_spotify_play"],r"(?:play)(?:\s(album|track|playlist))?\s(.*)")
@SpotifySkillValidation
async def Play(phrase, args):
    type_to_play = "track"
    item_name = args[1]

    if args[0]:
        type_to_play = args[0].lower()

    result = requests.get(url="https://api.spotify.com/v1/search", headers=header_data, params={
        "q": item_name,
        "type": [type_to_play]
    }).json()

    query = '{}s'.format(type_to_play)
    if result[query] and len(result[query]['items']) > 0:
        if type_to_play == 'track':
            requests.put(url="https://api.spotify.com/v1/me/player/play", headers=header_data, json={
                'uris': [result[query]['items'][0]['uri']]
            }).content
        else:

            requests.put(url="https://api.spotify.com/v1/me/player/play", headers=header_data, json={
                'context_uri': result[query]['items'][0]['uri'],
                'offset': {'position': 0}
            })

        DisplayUiMessage("Playing {}".format(result[query]['items'][0]['name']))


@Skill(["skill_spotify_add"],r"(?:add|queue)\s(.*)")
@SpotifySkillValidation
async def AddToQueue(phrase, args):
    result = requests.get(url="https://api.spotify.com/v1/search", headers=header_data, params={
        "q": args[0],
        "type": ['track']
    }).json()

    if result['tracks'] and len(result['tracks']['items']) > 0:
        requests.post(
            url="https://api.spotify.com/v1/me/player/queue?uri={}".format(result['tracks']['items'][0]['uri']),
            headers=header_data)
        DisplayUiMessage("Queued {}".format(result['tracks']['items'][0]['name']))


@Skill(["skill_spotify_volume"],r"(?:music volume|volume music)(?:\s(album|track|playlist))?\s([a-z\s]+?)(?:\s(?:percent$)|$)")
@SpotifySkillValidation
async def ModifyVolume(phrase, args):
    try:
        volume = int(w2n.word_to_num(args[0].strip()))

        if volume < 0 or volume > 100:
            raise Exception('Volume must be a number between 0 and 100 inclusive')

        requests.put(
            url="https://api.spotify.com/v1/me/player/volume?volume_percent={}".format(volume),
            headers=header_data)
        TextToSpeech('Set music volume to {}, Percent.'.format(num2words(volume)))
    except Exception as e:
        print(e)
        pass
