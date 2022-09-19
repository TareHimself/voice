from datetime import  datetime, timezone
from events import global_emitter
from skills import RegisterSkill
import webbrowser


def DisplayTime(phrase, match):
    global_emitter.emit('say', "The time is {}"
                        .format(datetime.now(timezone.utc).astimezone().strftime('%H:%M')),True)


RegisterSkill(DisplayTime, r"^(time|what (time is it|is the time))$")
