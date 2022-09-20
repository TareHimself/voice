from datetime import  datetime, timezone
from events import global_emitter
from skills import RegisterSkill
from num2words import num2words


def DisplayTime(phrase, match):
    current_time = datetime.now(timezone.utc).astimezone()
    time_to_say = 'The time is '

    for word in (current_time.strftime('%I %M') + (" ai em." if current_time.hour < 12 else " pea em.")).split():
        if word.isdigit():
            time_to_say += num2words(int(word)) + " "
        else:
            time_to_say += word + " "

    print(time_to_say)
    global_emitter.emit('do_speech', time_to_say)
    global_emitter.emit('say', "The time is {}".format(current_time.strftime('%I:%M %p')),True)



RegisterSkill(DisplayTime, r"^(time|what (time is it|is the time))$")
