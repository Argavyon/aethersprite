"GitHub URL command"

# local
from .. import bot, log


@bot.command(brief='GitHub URL for bot source code, feature requests')
async def github(ctx):
    """
    This bot is running on ncfacbot, an open source Nexus Clash faction bot software built with discord.py. My source code is available for free. Contributions in the form of code, bug reports, and feature requests are all welcome.  

    https://github.com/haliphax/ncfacbot
    """

    await ctx.send('For source code, feature requests, and bug reports, visit '
                   'https://github.com/haliphax/ncfacbot')
    log.info(f'{ctx.author} requested GitHub URL')
