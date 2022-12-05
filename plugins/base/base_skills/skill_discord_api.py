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


async def send_data_to_discord(msg, discord_message: dict):
    payload = {
        "content": msg,
        "message_reference": {
            "message_id": discord_message['id'],
            "channel_id": discord_message['channel_id'],
        }
    }
    requests.post(
        f"http://localhost:8099/discord/channels/{discord_message['channel_id']}/messages", json=payload)
    log("Discord Response ::", msg)


follow_up_callback = None

pending_followups = {}


class DiscordContext(AssistantContext):
    def __init__(self, discord_message) -> None:
        super().__init__()
        self.discord_message = discord_message
        self.discord_user_id = discord_message['author']['id']

    async def get_followup(self, timeout_secs=0):
        global pending_followups
        loop = asyncio.get_event_loop()
        task_return = asyncio.Future()
        task_id = uuid.uuid1()

        def on_results_recieved(msg):
            global pending_followups
            nonlocal task_return

            if pending_followups.get(self.discord_user_id, None) is not None:
                stop_timer(task_id)
                loop.call_soon_threadsafe(task_return.set_result, msg)
                del pending_followups[self.discord_user_id]

        def OnTimeout():
            global pending_followups
            nonlocal task_return
            if pending_followups.get(self.discord_user_id, None) is not None:
                loop.call_soon_threadsafe(task_return.set_result, None)
                del pending_followups[self.discord_user_id]

        pending_followups[self.discord_user_id] = on_results_recieved

        if timeout_secs > 0:
            start_timer(timer_id=task_id, length=timeout_secs,
                        callback=OnTimeout)

        result = await task_return

        if result is None:
            return None

        self.discord_message = result

        return self.discord_message['content']

    async def handle_response(self, resp: str):
        await send_data_to_discord(resp, self.discord_message)

    async def handle_parse_error(self, phrase: str):
        await send_data_to_discord(phrase, self.discord_message)


@ServerHandler(r'/discord/message')
class DiscordMessageHandler(tornado.web.RequestHandler):

    async def post(self):
        global pending_followups
        discord_message = json_decode(self.request.body)
        self.write(json.dumps({"body": "Ok"}))

        if discord_message['author']['id'] == "1027027399474425896":
            return

        content: str = discord_message.get('content', '')

        if len(content) <= 0:
            return

        if discord_message['author']['id'] in pending_followups.keys():
            pending_followups[discord_message['author']['id']](discord_message)
            return

        if content.strip().lower().startswith('alice'):
            content = content[5:].strip()
        elif discord_message.get('guild_id', None) is not None:
            return

        skill_ids = await try_start_skill(content, DiscordContext, discord_message)
