import json

import tornado.web
from tornado.escape import json_decode
from core.events import gEmitter
from core import constants
from core.decorators import ServerHandler
from core.utils import TryStartSkill
from core.logger import log


@ServerHandler(r'/telegram/webhook')
class TelegramWebhookHandler(tornado.web.RequestHandler):

    async def post(self):
        content = json_decode(self.request.body)

        self.write(json.dumps({"body": "Ok"}))

        if content is not None and content.get('message', None) is not None:
            message = content.get('message')
            if message.get('text', None) is not None:
                actual_message = message.get('text', None)
                skill_ids = await TryStartSkill(actual_message)
                log('Start Skill Result :', skill_ids)
                # gEmitter.emit(constants.EVENT_SEND_PHRASE_TO_ASSISTANT,
                #               f"{constants.WAKE_WORD} {actual_message}", True)
