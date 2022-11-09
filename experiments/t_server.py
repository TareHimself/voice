import asyncio
from threading import Thread
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        self.write("Hello, world")


class PostHandler(tornado.web.RequestHandler):
    async def post(self):
        print(self.request.body.decode())
        self.write("Hello, world")


def make_app():
    e = tornado.web.Application([
        (r"/", MainHandler),
    ])

    return e


app = None


async def main():
    pass


def doInputs():
    global app
    while True:
        action = input('What do you want to do :\n')
        if action == '1':
            print(app.default_router.add_rules([
                (r"/test", PostHandler),
            ]))


t = Thread(target=doInputs, daemon=True)
t.start()

if __name__ == "__main__":
    asyncio.run(main())
