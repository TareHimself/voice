import asyncio
import json
from os import mkdir, path
import uuid
from core.assistant import AssistantContext
import requests
import tornado.web
from tornado.escape import json_decode
from core.events import gEmitter
from core import constants
from core.decorators import AssistantLoader, ServerHandler
from core.threads.timer import start_timer, stop_timer
from core.utils import try_start_skill, run_in_thread
from core.logger import log
from plugins.base.constants import PLUGIN_ID

config = None
TELEGRAM_PATH = path.join(constants.DIRECTORY_DATA, PLUGIN_ID, 'telegram')

TELEGRAM_CONFIG_PATH = path.join(TELEGRAM_PATH, 'auth.json')


@AssistantLoader
async def create_telegram_auth():
    global config
    if not path.exists(TELEGRAM_PATH):
        mkdir(TELEGRAM_PATH)

    if not path.exists(TELEGRAM_CONFIG_PATH):
        config = {
            'auth': "",
        }
        with open(TELEGRAM_CONFIG_PATH, 'w') as f:
            f.write(json.dumps(config, indent=2))
    else:
        with open(TELEGRAM_CONFIG_PATH, 'r') as f:
            config = json.load(f)


async def send_data_to_telegram(msg):
    if len(config.get('auth', '')) > 0:
        requests.get(
            f"https://api.telegram.org/bot{config.get('auth')}/sendMessage?chat_id=1537501354&text={msg}")


follow_up_callback = None


class TelegramContext(AssistantContext):
    def __init__(self) -> None:
        super().__init__()

    async def get_followup(self, timeout_secs=0):
        global follow_up_callback
        loop = asyncio.get_event_loop()
        task_return = asyncio.Future()
        task_id = uuid.uuid1()

        def on_results_recieved(msg):
            global follow_up_callback
            nonlocal task_return

            if follow_up_callback:
                stop_timer(task_id)
                loop.call_soon_threadsafe(task_return.set_result, msg)
                follow_up_callback = None

        def OnTimeout():
            global follow_up_callback
            nonlocal task_return
            if follow_up_callback:
                loop.call_soon_threadsafe(task_return.set_result, None)
                follow_up_callback = None

        follow_up_callback = on_results_recieved

        if timeout_secs > 0:
            start_timer(timer_id=task_id, length=timeout_secs,
                        callback=OnTimeout)

        result = await task_return

        return result

    async def handle_response(self, resp: str):
        await send_data_to_telegram(resp)

    async def handle_parse_error(self, phrase: str):
        await send_data_to_telegram(phrase)


@ServerHandler(r'/telegram/webhook')
class TelegramWebhookHandler(tornado.web.RequestHandler):

    async def post(self):
        global follow_up_callback
        content = json_decode(self.request.body)

        self.write(json.dumps({"body": "Ok"}))

        if content is not None and content.get('message', None) is not None:
            message = content.get('message')
            if message.get('text', None) is not None:
                actual_message: str = message.get('text', None)
                if follow_up_callback:
                    follow_up_callback(actual_message)
                    return
                if actual_message.lower().startswith(constants.WAKE_WORD):
                    actual_message = actual_message[len(
                        constants.WAKE_WORD):len(actual_message)].strip()
                if len(actual_message) > 0:
                    skill_ids = await try_start_skill(actual_message, TelegramContext)
