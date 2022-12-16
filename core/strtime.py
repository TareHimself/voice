import re
from datetime import datetime, tzinfo, timedelta
from core.numwrd import wrd2num, convertTextNumbersToDigits

STRING_TO_TIME_EXPR_1 = re.compile(
    r"(tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)?\s?(?:at|by)\s?([a-z]+)\s?([a-z]{3,}\s[a-z]{3,}|[a-z]{3,})?\s?(pm|am)?")
STRING_TO_TIME_EXPR_2 = re.compile(
    r"(?:.*in (?:an? )?)?(?:([0-9]{1,})?\s?(days?|hours?|minutes?|seconds?))?(?: and | )?(?:([0-9]{1,})?\s?(days?|hours?|minutes?|seconds?))?(?: and | )?(?:([0-9]{1,})?\s?(days?|hours?|minutes?|seconds?))?(?: and | )?(?:([0-9]{1,})?\s?(days?|hours?|minutes?|seconds?))?")
WEEKDAYS = ['monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday']


def string_to_time(text: str, tz: tzinfo = None):
    text = convertTextNumbersToDigits(text).lower().strip()
    match_attempt = re.match(
        STRING_TO_TIME_EXPR_1,
        text)

    if match_attempt:
        day, hour, minute, am_pm = match_attempt.groups()

        start = datetime.now(tz=tz)

        if day == "tomorrow":
            start += timedelta(days=1)
        elif day.lower() in WEEKDAYS:
            target = WEEKDAYS.index(day.lower())
            current = start.today().weekday()
            final = ((target + 7) -
                     current) if target < current else (target - current)
            start += timedelta(days=final)

        if hour is not None:
            hour = wrd2num(hour)
            if am_pm is not None and am_pm.lower() == "pm":
                hour = hour + 12

            start.replace(hour=hour)
        if minute is not None:
            minute = wrd2num(minute)
            start.replace(minute=minute)

        return start

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
                    value = int(value)
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


def time_to_human_str(t: datetime, tz: tzinfo = None):
    pass
