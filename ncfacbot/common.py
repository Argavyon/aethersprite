"Common functions module"

# stdlib
import calendar
from collections import namedtuple
from datetime import datetime, timezone
from math import ceil, floor
import re
# 3rd party
from discord.ext.commands import check, command as command_

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
# List of checks to run against all commands
global_checks = []


def command(*args, **kwargs):
    """
    Decorator to add global checks to new commands. This is just a thin
    wrapper around :func:`discord.ext.commands.command`, and will accept the
    same arguments.
    """

    def wrap(f):
        global global_checks

        first = True
        check_stack = []

        for c in global_checks:
            if first:
                check_stack.append(
                    check(c)(command_(*args, **kwargs)(f)))
                first = False
            else:
                check_stack.append(check(c)(check_stack[-1]))

        return check_stack[-1]

    return wrap


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


def global_check(f):
    "Decorator to add function to list of checks to run for each command."

    global global_checks

    if f not in global_checks:
        global_checks.append(f)

    return f


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

    seconds = ceil(ts)
    until = []

    if seconds >= DAY:
        days = floor(seconds / DAY)
        until.append(f'{days} day{"s" if days > 1 else ""}')
        seconds = seconds % DAY

    if seconds >= HOUR:
        hours = floor(seconds / HOUR)
        until.append(f'{hours} hour{"s" if hours > 1 else ""}')
        seconds = seconds % HOUR

    if seconds >= MINUTE:
        minutes = floor(seconds / MINUTE)
        until.append(f'{minutes} minute{"s" if minutes > 1 else ""}')
        seconds = seconds % MINUTE

    if seconds > 0:
        until.append(f'{seconds} second{"s" if seconds > 1 else ""}')

    return ', '.join(until)


def startup(f):
    """
    Decorator to add function to list of handlers to run for the ``on_ready``
    event. The first argument of the function (not counting ``self`` if the
    function is a method) will be provided with a reference to the bot. To
    decorate a method, assign the handler during ``__init__``.

    .. code:: python

        from discord.ext.commands import Cog
        from ncfacbot.common import startup

        class SomeClass(Cog):
            def __init__(self, bot):
                self.bot = bot
                self.on_ready = startup(self.on_ready)

            def on_ready(self, _):
                # don't care about the bot parameter here, but still have to include it
                # to avoid exceptions
                pass

        @startup
        def on_ready(bot):
            # since we're not a Cog, we need the bot reference to do stuff
            pass
    """

    global startup_handlers

    if f not in startup_handlers:
        startup_handlers.append(f)

    return f
