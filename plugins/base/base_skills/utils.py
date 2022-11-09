import datetime

from core.numwrd import num2wrd


def TimeToSttText(t: datetime):
    [hour, minute] = t.strftime('%I|%M').split('|')

    if hour.startswith('0'):
        if hour.startswith('00'):
            hour = num2wrd(12)
        else:
            hour = num2wrd(int(hour[1]))
    else:
        hour = num2wrd(int(hour))

    if minute.startswith('0'):
        if minute.startswith('00'):
            minute = ""
        else:
            minute = "oh {}".format(num2wrd(int(minute[1])))
    else:
        minute = num2wrd(int(minute))

    is_daytime = t.hour < 12
    return "{} {} ,{}".format(hour, minute, "ai em" if is_daytime else "pee em")
