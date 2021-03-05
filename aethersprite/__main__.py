# stdlib
import logging
from os import environ
from random import seed
from sys import stdout
from typing import Optional
# 3rd party
from discord import Activity, ActivityType
from discord import DMChannel, Member, RawReactionActionEvent
from discord.ext.commands import (Bot, CheckFailure, command, CommandNotFound,
                                  Context, DefaultHelpCommand,
                                  when_mentioned_or,)
# local
from . import config, log

# logging stuff
streamHandler = logging.StreamHandler(stdout)
streamHandler.setFormatter(logging.Formatter(
    '{asctime} {levelname:<7} <{module}.{funcName}> {message}', style='{'))
log.addHandler(streamHandler)
log.setLevel(getattr(logging, environ.get('LOGLEVEL', 'INFO')))

_help = config['bot']['help_command']

#: Activity on login
activity = Activity(name=f'!{_help}', type=ActivityType.listening)


def get_ending_note(self):
    return (f'Type !{_help} <command> for more info on a command.\n'
            f'You can also type !{_help} <category> for more info on a '
            'category.')

DefaultHelpCommand.get_ending_note = get_ending_note


@command(name=_help, hidden=True)
async def aehelp(ctx: Context, command: Optional[str] = None):
    if command is None:
        await ctx.send_help()
    else:
        await ctx.send_help(command)


#: The bot itself
bot = Bot(command_prefix=when_mentioned_or('!'))


@bot.event
async def on_connect():
    log.info('Connected to Discord')


@bot.event
async def on_disconnect():
    log.info('Disconnected')


@bot.event
async def on_command_error(ctx: Context, error: Exception):
    "Suppress command check failures and invalid commands."

    if isinstance(error, CheckFailure):
        return

    if isinstance(error, CommandNotFound):
        if isinstance(ctx.channel, DMChannel):
            return

        cog = ctx.bot.get_cog('alias')

        if cog is None:
            return

        guild = str(ctx.guild.id)
        aliases = cog.aliases[guild] if guild in cog.aliases else None

        if aliases is None:
            return

        name = ctx.message.content \
                .replace(ctx.prefix, '').split(' ')[0].strip()

        if name not in aliases:
            return

        cmd = ctx.bot.get_command(aliases[name])

        if cmd is None:
            return

        ctx.command = cmd

        return await ctx.bot.invoke(ctx)

    raise error


@bot.event
async def on_member_join(member: Member):
    "Fire on_member_join handlers."

    from .handlers import MemberJoinHandlers

    log.debug(f'{member!r}')

    for f in set(MemberJoinHandlers.handlers):
        await f(member)


@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    "Fire on_raw_reaction_add handlers."

    from .handlers import RawReactionAddHandlers

    log.debug(f'{payload!r}')

    for f in set(RawReactionAddHandlers.handlers):
        await f(payload)


@bot.event
async def on_raw_reaction_remove(payload: RawReactionActionEvent):
    "Fire on_raw_reaction_add handlers."

    from .handlers import RawReactionAddHandlers

    log.debug(f'{payload!r}')

    for f in set(RawReactionAddHandlers.handlers):
        await f(payload)


@bot.event
async def on_ready():
    "Update presence and fire up registered startup handlers."

    from .handlers import ReadyHandlers

    log.info(f'Logged in as {bot.user}')
    await bot.change_presence(activity=activity)

    for f in set(ReadyHandlers.handlers):
        await f(bot)


@bot.event
async def on_resumed():
    log.info('Connection resumed')


# redundant, but one last check in case someone wants to get real shifty and
# do something that requires them to import __main__ from another entry point
def entrypoint():
    "aethersprite main entry point."

    token = config['bot'].get('token', environ.get('DISCORD_TOKEN', None))
    # need credentials
    assert token is not None, \
        'bot.token not in config and DISCORD_TOKEN not in env variables'
    # for any commands or scheduled tasks, etc. that need random numbers
    seed()
    bot.remove_command('help')
    bot.add_command(aehelp)

    # load extensions
    for ext in config['bot']['extensions']:
        bot.load_extension(ext)

    # here we go!
    bot.run(token)

if __name__ == '__main__':
    entrypoint()
