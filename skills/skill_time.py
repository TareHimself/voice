from datetime import  datetime, timezone
from events import global_emitter
from skills import RegisterSkill, skill
from num2words import num2words

@skill(r"^(time|what (time is it|is the time))$")
def DisplayTime(phrase, match):
    current_time = datetime.now(timezone.utc).astimezone()
    time_to_say = 'The time is '

    for word in (current_time.strftime('%I %M') + (" ai em." if current_time.hour < 12 else " pea em.")).split():
        if word.isdigit():
            time_to_say += num2words(int(word)) + " "
        else:
            time_to_say += word + " "

    global_emitter.emit('do_speech', time_to_say)
    global_emitter.emit('say', "The time is {}".format(current_time.strftime('%I:%M %p')),True)
