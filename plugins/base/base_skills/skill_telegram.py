import json
from os import mkdir, path
from core.assistant import AssistantContext
import requests
import tornado.web
from tornado.escape import json_decode
from core.events import gEmitter
from core import constants
from core.decorators import AssistantLoader, ServerHandler
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


class TelegramContext(AssistantContext):
    def __init__(self) -> None:
        super().__init__()

    async def handle_response(self, resp: str):
        await send_data_to_telegram(resp)

    async def handle_parse_error(phrase: str):
        await send_data_to_telegram(phrase)


@ServerHandler(r'/telegram/webhook')
class TelegramWebhookHandler(tornado.web.RequestHandler):

    async def post(self):
        content = json_decode(self.request.body)

        self.write(json.dumps({"body": "Ok"}))

        if content is not None and content.get('message', None) is not None:
            message = content.get('message')
            if message.get('text', None) is not None:
                actual_message = message.get('text', None)
                skill_ids = await try_start_skill(actual_message, TelegramContext)
                log('Start Skill Result :', skill_ids)
                # gEmitter.emit(constants.EVENT_SEND_PHRASE_TO_ASSISTANT,
                #               f"{constants.WAKE_WORD} {actual_message}", True)
