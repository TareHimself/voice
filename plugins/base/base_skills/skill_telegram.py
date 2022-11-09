

import tornado.web
from core.decorators import ServerHandler
from core.logger import log
import json


@ServerHandler(r'/telegram/webhook')
class TelegramWebhookHandler(tornado.web.RequestHandler):
    async def post(self):

        self.finish(json.dumps({"body": "Ok"}))
