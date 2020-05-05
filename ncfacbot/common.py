"Common functions module"

# stdlib
from asyncio import get_event_loop
import calendar
from collections import namedtuple
from datetime import datetime, timezone
from functools import wraps
from math import ceil, floor
import re
# 3rd party
from discord import DMChannel
from discord.ext.commands import check, command as command_, Context
# local
from . import bot
from .lobotomy import check_lobotomy

# constants
#: One minute in seconds
MINUTE = 60
#: One hour in seconds
HOUR = MINUTE * 60
#: One day in seconds
DAY = HOUR * 24
#: 15 minutes in seconds
FIFTEEN_MINS = MINUTE * 15
#: Thumbs down emoji
THUMBS_DOWN = '\U0001F44E'
#: Police officer emoji
POLICE_OFFICER = '\U0001F46E'
#: Formatting string for datetime objects
DATETIME_FORMAT = '%a %Y-%m-%d %H:%M:%S %Z'

# structs
#: Fake a context for use in certain functions that expect one
FakeContext = namedtuple('FakeContext', ('guild',))

# List of functions to run on startup during on_ready
startup_handlers = []


def command(*args, **kwargs):
    "Decorator to add default checks to new commands."

    def wrap(f):
        return check(check_lobotomy)(command_(*args, **kwargs)(f))

    return wrap


async def channel_only(ctx):
    "Check for bot commands that should only operate in a channel"

    if type(ctx.channel) is DMChannel:
        await ctx.send('This command must be used in a channel.')

        return False

    return True


def get_timespan_chunks(string):
    """
    Search string for chunks of timespan parameters, like 5d 10h 15m, etc.

    :param string: The string to search
    :returns: ``(days: int, hours: int, minutes: int)``
    :rtype: tuple
    """

    s = re.search(r'.*?(-?\d+)d.*', string)
    days = int(s.groups()[0]) if s else 0
    s = re.search(r'.*?(-?\d+)h.*', string)
    hours = int(s.groups()[0]) if s else 0
    s = re.search(r'.*?(-?\d+)m.*', string)
    minutes = int(s.groups()[0]) if s else 0

    return (days, hours, minutes)


def get_next_tick(n=1):
    """
    Calculate future tick as datetime in GMT.

    :param n: The number of ticks forward to calculate
    :type n: int
    :returns: The time of the calculated tick
    :rtype: datetime
    """

    now = calendar.timegm(datetime.now(timezone.utc).timetuple())
    tick_stamp = (now + (n * FIFTEEN_MINS)) - (now % FIFTEEN_MINS)

    return datetime.fromtimestamp(tick_stamp, tz=timezone.utc)


def normalize_username(author):
    """
    Normalize username for use in messages. If the user has a nick set, that
    will be used; otherwise, their plain username will be returned.

    :param author: The User object to normalize
    :returns: The normalized name
    :rtype: str
    """

    name = author.name

    if hasattr(author, 'nick') and author.nick is not None:
        name = author.nick

    return name


def seconds_to_str(ts):
    """
    Convert a span of seconds into a human-readable format (e.g. "5 day(s)
    8 hour(s) 12 minute(s) 36 second(s)").

    :param ts: The span to convert
    :type ts: int
    :returns: The human-readable representation
    :rtype: str
    """

    diff = ceil(ts)
    until = ''

    if diff >= DAY:
        until += f'{floor(diff / DAY)} day(s) '
        diff = diff % DAY

    if diff >= HOUR:
        until += f'{floor(diff / HOUR)} hour(s) '
        diff = diff % HOUR

    if diff >= MINUTE:
        until += f'{floor(diff / MINUTE)} minute(s) '
        diff = diff % MINUTE

    if diff > 0:
        until += f'{diff} second(s) '

    return until.strip()


def startup(f):
    "Decorator to add function to list of handlers to run for on_ready"

    global startup_handlers

    startup_handlers.append(f)

    return f
