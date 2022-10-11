import re
from datetime import datetime, tzinfo, timedelta
from num_wrd import wrd2num

STRING_TO_TIME_EXPR_1 = r"(tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)?\s?(?:at|by)\s?([a-z]+)\s?([a-z]{3,}\s[a-z]{3,}|[a-z]{3,})?\s?(pm|am)?"
STRING_TO_TIME_EXPR_2 = r"(?:in (?:an? )?)(?:([a-z]+|[a-z]+\s[a-z]+)?\s?(days?|hours?|minutes?|seconds?))?(?:(?:[\s,]+)?(?:and)?(?:[\s,]+)?)?(?:([a-z]+|[a-z]+\s[a-z]+)?\s?(days?|hours?|minutes?|seconds?))?(?:(?:[\s,]+)?(?:and)?(?:[\s,]+)?)?(?:([a-z]+|[a-z]+\s[a-z]+)?\s?(days?|hours?|minutes?|seconds?))?(?:(?:[\s,]+)?(?:and)?(?:[\s,]+)?)?(?:([a-z]+|[a-z]+\s[a-z]+)?\s?(days?|hours?|minutes?|seconds?))?"


def stringToTime(text: str, tz: tzinfo = None):
    text = text.lower().strip()
    match_attempt = re.match(
        STRING_TO_TIME_EXPR_1,
        text)

    if match_attempt:
        day, hour, minute, am_pm = match_attempt.groups()
        print(day, hour, minute, am_pm)

        start = datetime.now(tz=tz)

        #datetime.
        datetime.today().weekday()
        print(datetime.today().isoweekday())

    else:
        start = datetime.now(tz=tz)
        current = start
        match_attempt = re.match(STRING_TO_TIME_EXPR_2, text)
        if match_attempt:
            delta = timedelta(0, 0, 0, 0, 0, 0, 0)
            data = list(match_attempt.groups())
            for i in range(len(data) // 2):
                value = data[i * 2]
                unit = data[(i * 2) + 1]

                if unit and unit.endswith('s'):
                    unit = unit[:-1]

                if value and unit:
                    value = wrd2num(value)
                elif unit:
                    value = 1

                if unit == 'day':
                    delta = timedelta(days=value)
                if unit == 'hour':
                    delta = timedelta(hours=value)
                elif unit == 'minute':
                    delta = timedelta(minutes=value)
                elif unit == 'second':
                    delta = timedelta(seconds=value)

                current = delta + current
                delta = timedelta(0, 0, 0, 0, 0, 0, 0)
            return current
        else:
            return None