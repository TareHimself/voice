

import json

import tornado.web
from tornado.escape import json_decode
from core.events import gEmitter
from core import constants
from core.decorators import ServerHandler
from core.logger import log


@ServerHandler(r'/telegram/webhook')
class TelegramWebhookHandler(tornado.web.RequestHandler):

    async def post(self):
        content = json_decode(self.request.body)
        if content != None and content.get('message', None) != None:
            message = content.get('message')
            if message.get('text', None) != None:
                actual_message = message.get('text', None)
                gEmitter.emit(constants.EVENT_SEND_PHRASE_TO_ASSISTANT,
                              f"{constants.WAKE_WORD} {actual_message}", True)

        self.finish(json.dumps({"body": "Ok"}))
