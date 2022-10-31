from core.events import gEmitter, ThreadEmitter


class InputThread(ThreadEmitter):

    def __init__(self):
        super(InputThread, self).__init__()

    def run(self):
        try:
            while True:
                user_input = input('assistant input: ')
                if len(user_input.strip()) > 0:
                    gEmitter.emit('user_input', user_input)
        except KeyboardInterrupt:
            pass
