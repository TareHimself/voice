from events import global_emitter
from events.thread_emitter import ThreadEmitter


class InputThread(ThreadEmitter):

    def __init__(self):
        super(InputThread, self).__init__()


    def run(self):
        while True:
            user_input = input('assistant input: ')
            if len(user_input.strip()) > 0:
                global_emitter.emit('user_input',user_input)