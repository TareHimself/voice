import asyncio
import base64
import tornado.web
from datetime import datetime, timedelta
import json
import webbrowser
import aiohttp
import requests
from core.logger import log
from core.numwrd import num2wrd, wrd2num
from core.decorators import Skill, AssistantLoader, ServerHandler
from core.singletons import GetSingleton
from core.constants import DIRECTORY_DATA, SINGLETON_SERVER_ID
from urllib.parse import urlencode
from os import path, mkdir
from plugins.base.constants import PLUGIN_ID
from core.assistant import SkillEvent
from plugins.base.text_to_speech import TextToSpeech
from core.events import gEmitter

SPOTIFY_PATH = path.join(DIRECTORY_DATA, PLUGIN_ID, 'spotify')

SPOTIFY_AUTH_PATH = path.join(SPOTIFY_PATH, 'auth.json')

SPOTIFY_CONFIG_PATH = path.join(SPOTIFY_PATH, 'config.json')

spotify_auth = None
header_data = None
spotify_auth_refresh = None
config = None
server = GetSingleton(SINGLETON_SERVER_ID)


@AssistantLoader
async def SetSpotifyAuth():
    global spotify_auth
    global config
    if not path.exists(SPOTIFY_PATH):
        mkdir(SPOTIFY_PATH)

    if path.exists(SPOTIFY_AUTH_PATH):
        with open(SPOTIFY_AUTH_PATH, 'r') as f:
            spotify_auth = json.load(f)

    if not path.exists(SPOTIFY_CONFIG_PATH):
        config = {
            'id': "",  # str(input('Please input your spotify client id: ')),
            # str(input('Please input your spotify client secrete: ')),
            'secret': "",
            # str(input('Please input your spotify callback url: ')),
            'uri': "",
            'scope': "user-modify-playback-state"
        }
        with open(SPOTIFY_CONFIG_PATH, 'w') as f:
            f.write(json.dumps(config, indent=2))
    else:
        with open(SPOTIFY_CONFIG_PATH, 'r') as f:
            config = json.load(f)


def UpdateHeader(auth):
    global header_data
    header_data = {
        "Authorization": "{} {}".format(auth['token_type'], auth['access_token']),
        'Content-Type': 'application/json',
    }


@ServerHandler(r'/spotify')
class SpotifyAuthHandler(tornado.web.RequestHandler):
    async def get(self):
        global config
        code = self.get_query_argument('code', None)

        self.finish("recieved")
        url = "https://accounts.spotify.com/api/token"

        payload = {
            "code": code,
            "redirect_uri": config['uri'],
            'grant_type': "authorization_code"
        }

        auth_code = config['id'] + \
            ':' + config['secret']
        headers = {
            "Authorization": "Basic " + base64.urlsafe_b64encode((auth_code).encode('ascii')).decode('ascii'),
            'Content-Type': 'application/x-www-form-urlencoded'}

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, data=payload) as resp:
                auth_data = await resp.json()
                gEmitter.emit('plugin_base_on_spotify_auth', auth_data)


def GetSpotifyAuth():
    loop = asyncio.get_event_loop()
    global config
    task_return = asyncio.Future()
    authorize_url = "https://accounts.spotify.com/authorize?response_type=code&" + urlencode(
        {'client_id': config['id'], 'scope': config['scope'],
         'redirect_uri': config['uri']})

    def OnAuthRecieved(auth):
        loop.call_soon_threadsafe(task_return.set_result, auth)

    gEmitter.once('plugin_base_on_spotify_auth', OnAuthRecieved)

    webbrowser.open(authorize_url, new=2)

    return task_return


async def ValidateSpotifyAuth():
    global spotify_auth
    global spotify_auth_refresh
    if not spotify_auth:
        spotify_auth = await GetSpotifyAuth()
        spotify_auth_refresh = datetime.utcnow(
        ) + timedelta(seconds=spotify_auth['expires_in'])
        spotify_auth['expires_at'] = spotify_auth_refresh.isoformat()
        del spotify_auth['expires_in']
        UpdateHeader(spotify_auth)
        with open(SPOTIFY_AUTH_PATH, "w") as outfile:
            json.dump(spotify_auth, outfile, indent=4)

    if not spotify_auth_refresh:
        spotify_auth_refresh = datetime.fromisoformat(
            spotify_auth['expires_at'])
        UpdateHeader(spotify_auth)
        return await ValidateSpotifyAuth()

    utc_now = datetime.utcnow()
    if spotify_auth_refresh < utc_now:
        payload = {
            'grant_type': 'refresh_token',
            "refresh_token": spotify_auth['refresh_token'],
            "client_id": config['id']
        }

        auth_code = config['id'] + \
            ':' + config['secret']
        headers = {"Authorization": "Basic " + base64.urlsafe_b64encode(auth_code.encode('ascii')).decode('ascii'),
                   'Content-Type': 'application/x-www-form-urlencoded'}
        url = "https://accounts.spotify.com/api/token"
        auth_data = requests.post(
            url=url, headers=headers, data=payload).json()
        spotify_auth_refresh = utc_now + \
            timedelta(seconds=auth_data['expires_in'])
        spotify_auth['access_token'] = auth_data['access_token']
        spotify_auth['expires_at'] = spotify_auth_refresh.isoformat()
        UpdateHeader(spotify_auth)
        with open(SPOTIFY_AUTH_PATH, "w") as outfile:
            json.dump(spotify_auth, outfile, indent=4)

    return True


def SpotifySkillValidation(f):
    async def inner(*args, **kwargs):
        if await ValidateSpotifyAuth():
            await f(*args, **kwargs)
        return

    return inner


@Skill(["skill_spotify_pause"])
@SpotifySkillValidation
async def Pause(e: SkillEvent, args):
    requests.put(url="https://api.spotify.com/v1/me/player/pause",
                 headers=header_data)


@Skill(["skill_spotify_resume"])
@SpotifySkillValidation
async def Resume(e: SkillEvent, args):
    requests.put(url="https://api.spotify.com/v1/me/player/play",
                 headers=header_data)


@Skill(["skill_spotify_skip"])
@SpotifySkillValidation
async def Skip(e: SkillEvent, args):
    requests.post(url="https://api.spotify.com/v1/me/player/next",
                  headers=header_data)


@Skill(["skill_spotify_play"], r"(?:play)(?:\s(album|track|playlist))?\s(.*)")
@SpotifySkillValidation
async def Play(e: SkillEvent, args):
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
            })
        else:

            requests.put(url="https://api.spotify.com/v1/me/player/play", headers=header_data, json={
                'context_uri': result[query]['items'][0]['uri'],
                'offset': {'position': 0}
            })

        log("Playing {}".format(
            result[query]['items'][0]['name']))


@Skill(["skill_spotify_add"], r"(?:add|queue)\s(.*)")
@SpotifySkillValidation
async def AddToQueue(e: SkillEvent, args):
    result = requests.get(url="https://api.spotify.com/v1/search", headers=header_data, params={
        "q": args[0],
        "type": ['track']
    }).json()

    if result['tracks'] and len(result['tracks']['items']) > 0:
        requests.post(
            url="https://api.spotify.com/v1/me/player/queue?uri={}".format(
                result['tracks']['items'][0]['uri']),
            headers=header_data)
        log("Queued {}".format(
            result['tracks']['items'][0]['name']))


@Skill(["skill_spotify_volume"], r"(?:music volume|volume music)\s([a-z\s]+?)(?:\s(?:percent$)|$)")
@SpotifySkillValidation
async def ModifyVolume(e: SkillEvent, args):
    volume = int(wrd2num(args[0]))

    if volume < 0 or volume > 100:
        raise Exception(
            'Volume must be a number between 0 and 100 inclusive')

    requests.put(
        url="https://api.spotify.com/v1/me/player/volume?volume_percent={}".format(
            volume),
        headers=header_data)
    await e.Respond(
        'Set music volume to {} Percent.'.format(num2wrd(volume)))
