"Lobotomy cog"

# stdlib
import typing
# 3rd party
from discord import DMChannel
from discord.ext import commands
from sqlitedict import SqliteDict
# local
from .. import log
from ..authz import require_admin
from ..common import command, global_check

#: Lobotomies database
lobotomies = SqliteDict('lobotomy.sqlite3', tablename='lobotomies',
                        autocommit=True)


class Lobotomy(commands.Cog, name='lobotomy'):

    "Lobotomy commands; enable and disable commands per-server and per-channel"

    def __init__(self, bot):
        self.bot = bot

    @command(name='lobotomy.add')
    @commands.check(require_admin)
    async def add(self, ctx, command, server: typing.Optional[bool] = False):
        """
        Disable the given command

        Disables <command> in this channel. If [server] is True, then the command is disabled on the entire server.
        """

        server_key = command.lower().strip()
        key = f'{server_key}#{ctx.channel.id}'
        guild = str(ctx.guild.id)

        if not ctx.guild.id in lobotomies:
            lobotomies[guild] = set([])

        lobs = lobotomies[guild]

        if (key in lobs and not server) \
                or (server_key in lobs and server):
            await ctx.send(f':newspaper: Already done.')

            return

        # if it's already in the opposite category (channel vs. server),
        # then clear it out
        if key in lobs and server:
            lobs.remove(key)
        elif server_key in lobs and not server:
            lobs.remove(server_key)

        lobs.add(server_key if server else key)
        lobotomies[guild] = lobs
        log.info(f'{ctx.author} lobotomized {server_key if server else key}')
        await ctx.send(f':brain: Done.')

    @command(name='lobotomy.clear')
    @commands.check(require_admin)
    async def clear(self, ctx, command, server: typing.Optional[bool] = False):
        """
        Enable the given command

        Enables <command> in this channel. If [server] is True, then the command is enabled on the entire server.
        """

        server_key = command.lower().strip()
        key = f'{server_key}#{ctx.channel.id}'
        guild = str(ctx.guild.id)
        lobs = lobotomies[guild] if guild in lobotomies else None

        if lobs is None:
            await ctx.send(':person_shrugging: None set.')

            return

        if (key in lobs and server) or (server_key in lobs and not server):
            await ctx.send(':thumbsdown: The opposite scope is '
                           'currently set.')

            return

        lobs.remove(server_key if server else key)
        lobotomies[guild] = lobs
        log.info(f'{ctx.author} cleared {server_key if server else key}')
        await ctx.send(':wastebasket: Cleared.')

    @command(name='lobotomy.list')
    @commands.check(require_admin)
    async def list(self, ctx, server: typing.Optional[bool] = False):
        """
        List all current channel's lobotomized commands

        If [server] is True, all lobotomies for all channels and the server will be shown, instead.
        """

        guild = str(ctx.guild.id)

        if guild not in lobotomies:
            lobotomies[guild] = []

        suffix = f'#{ctx.channel.id}'
        suffixlen = len(suffix)
        output = '**, **'.join([(l if server else l[:-suffixlen])
                                for l in lobotomies[guild]
                                if server or l.endswith(suffix)])

        if not len(output):
            output = 'None'

        log.info(f'{ctx.author} viewed {"server" if server else""} lobotomy '
                 'list')
        await ctx.send(f':medical_symbol: **{output}**')


@global_check
async def check_lobotomy(ctx):
    "Check that command has not been lobotomized before allowing execution."

    if type(ctx.channel) is DMChannel:
        # can't lobotomize commands via DM, since we need a guild to check
        # settings values
        return

    guild = str(ctx.guild.id)

    if guild not in lobotomies:
        # none set for this guild; bail
        return True

    keys = (ctx.command.name, f'{ctx.command.name}#{ctx.channel.id}')

    for k in keys:
        if k in lobotomies[guild]:
            log.warn(f'Suppressing lobotomized command from '
                     f'{ctx.author}: {ctx.command.name} in '
                     f'#{ctx.channel.name} ({ctx.guild.name})')

            return False

    return True


def setup(bot):
    bot.add_cog(Lobotomy(bot))
