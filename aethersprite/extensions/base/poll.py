"Poll cog"

# stdlib
from datetime import datetime
from functools import partial
import re
# 3rd party
import discord
from discord import Color, DMChannel, Embed, Message, Reaction, User
from discord.channel import TextChannel
from discord.ext.commands import check, command, Context
from discord.ext.commands.bot import Bot
from discord.guild import Guild
from discord.raw_models import RawReactionActionEvent
from sqlitedict import SqliteDict
# api
from aethersprite import data_folder, log
from aethersprite.authz import channel_only, owner, require_roles_from_setting
from aethersprite.common import THUMBS_DOWN
from aethersprite.filters import RoleFilter
from aethersprite.settings import register, settings

# constants
DIGIT_SUFFIX = '\ufe0f\u20e3'
SOLID_BLOCK = '\u2588'
SHADE_BLOCK = '\u2591'
WASTEBASKET = '\U0001f5d1'
CHECK_MARK = '\u2705'
PROHIBITED = '\U0001f6ab'
BAR_WIDTH = 20
POLL_EXPIRY = 86400 * 90  # 90 days

bot: Bot = None
# database
polls = SqliteDict(f'{data_folder}poll.sqlite3', tablename='polls',
                   autocommit=True)
# filters
create_filter = RoleFilter('poll.createroles')
vote_filter = RoleFilter('poll.voteroles')
# authz checks
authz_create = partial(require_roles_from_setting, setting='poll.createroles')
authz_vote = partial(require_roles_from_setting, setting='poll.voteroles')


@command()
@check(channel_only)
async def poll(ctx: Context, *, options: str):
    """
    Create a poll

    To create a poll, options must be provided. Separate options with commas. You may provide a prompt if you wish by encasing the first argument to the command in brackets.

    To delete a poll, use both the Delete and Confirm reactions. Only a moderator, administrator, or the creator of the poll may delete it.

    Examples:
        !poll The dress is green, The dress is gold
        !poll [Do you see what I see?] Yes, No
    """

    match = re.match(r'^(?:\[([^\]]+)\]\s*)?(.+)$', options)

    if match is None:
        await ctx.message.add_reaction(THUMBS_DOWN)
        log.warn(f'{ctx.author} Provided invalid arguments: {options}')

        return

    prompt, qstr = match.groups()
    count = 1
    opts = {}

    for s in qstr.split(','):
        emoji = f'{count}{DIGIT_SUFFIX}'
        opt = s.strip()
        opts[emoji] = {'text': opt, 'count': 0, 'votes': set([])}
        count += 1

    poll = {'timestamp': datetime.utcnow(),
            'author': ctx.author.display_name,
            'avatar': str(ctx.author.avatar_url),
            'prompt': prompt,
            'options': opts,
            'open': 1,
            'delete': set([]),
            'confirm': set([])}
    msg: Message = await ctx.send(embed=_get_embed(poll))

    for emoji in opts.keys():
        await msg.add_reaction(emoji)

    await msg.add_reaction(PROHIBITED)
    await msg.add_reaction(WASTEBASKET)
    await msg.add_reaction(CHECK_MARK)

    polls[msg.id] = poll
    log.info(f'{ctx.author} created poll: {poll!r}')


def _get_embed(poll):
    total = sum([int(o['count']) for _, o in poll['options'].items()])
    open = 'open' if poll['open'] else 'closed'
    prohib_text = 'Close' if poll['open'] else 'Open'
    embed = Embed(title=f':bar_chart: {poll["prompt"] or "Poll"}',
                  description=f'Poll is: {open}',
                  color=Color.blue())
    embed.set_author(name=poll['author'], icon_url=poll['avatar'])
    embed.set_footer(text=f'{PROHIBITED} {prohib_text} | '
                          f'{WASTEBASKET} Delete | {CHECK_MARK} Confirm')

    for key, opt in poll['options'].items():
        count = int(opt['count'])
        rawpct = round(0 if (total == 0 or count == 0)
                       else (count / total) * 100, 2)
        pct = 0 if (total == 0 or count == 0) else round((count / total) * 20)
        left = 20 - pct
        bar = f'{SOLID_BLOCK * pct}{SHADE_BLOCK * left}'
        embed.add_field(name=f'{key} {opt["text"]}', inline=False,
                        value=f'{bar} {opt["count"]} ({rawpct}%)')

    return embed


async def _update_poll(user: User, message: Message, emoji: str,
                       adjustment: int):
    poll = polls[message.id]
    opts = poll['options']
    opt = opts[emoji]
    opt['count'] += adjustment

    if adjustment > 0:
        if user.id in opt['votes']:
            opt['count'] -= adjustment
        else:
            opt['votes'].add(user.id)

    elif adjustment < 0:
        opt['votes'].remove(user.id)

    opts[emoji] = opt
    poll['options'] = opts
    polls[message.id] = poll
    await message.edit(embed=_get_embed(poll))


def _allowed(message: Message, user: User) -> bool:
    perms = user.permissions_in(message.channel)

    if perms.administrator or perms.manage_channels or perms.manage_guild \
            or owner == str(user) or message.author.id == user.id:
        return True

    role_ids = []
    setting = settings['poll.createroles'].get(user, raw=True)

    if setting is not None:
        role_ids = [int(r) for r in
                    settings['poll.createroles'].get(user)]

    for r in user.roles or []:
        if r.id in role_ids:
            return True

    return False

async def on_raw_reaction_add(payload: RawReactionActionEvent):
    "Handle on_reaction_add event."

    global bot

    if payload.user_id == bot.user.id or payload.message_id not in polls:
        return

    poll = polls[payload.message_id]
    user: User = await bot.fetch_user(payload.user_id)
    channel: TextChannel = await bot.fetch_channel(payload.channel_id)
    msg: Message = await channel.fetch_message(payload.message_id)

    if isinstance(msg.channel, DMChannel):
        return

    async def _delete():
        prompt = poll['prompt']
        delete = user.id in poll['delete']
        confirm =  user.id in poll['confirm']

        if delete and confirm:
            await msg.delete()
            del polls[msg.id]
            log.info(f'{user} deleted poll {msg.id} - {prompt}')

    if _allowed(msg, user):
        if payload.emoji.name == WASTEBASKET:
            poll['delete'].add(user.id)
            polls[msg.id] = poll
            await _delete()

            return

        if payload.emoji.name == CHECK_MARK:
            poll['confirm'].add(user.id)
            polls[msg.id] = poll
            await _delete()

            return

        if payload.emoji.name == PROHIBITED:
            poll['open'] = False
            polls[msg.id] = poll
            await msg.edit(embed=_get_embed(poll))

            return

    opts = poll['options']

    if payload.emoji.name not in opts or not poll['open']:
        await msg.remove_reaction(payload.emoji, user)

        return

    await _update_poll(user, msg, payload.emoji.name, 1)
    log.info(f'{user} voted for {payload.emoji} - {poll["prompt"]}')


async def on_raw_reaction_remove(payload: RawReactionActionEvent):
    "Handle on_reaction_remove event."

    if payload.message_id not in polls:
        return

    poll = polls[payload.message_id]
    user: User = await bot.fetch_user(payload.user_id)
    channel: TextChannel = await bot.fetch_channel(payload.channel_id)
    msg: Message = await channel.fetch_message(payload.message_id)

    if payload.emoji.name == WASTEBASKET:
        poll['delete'].remove(user.id)
        polls[msg.id] = poll

        return

    if payload.emoji.name == CHECK_MARK:
        poll['confirm'].remove(user.id)
        polls[msg.id] = poll

        return

    if payload.emoji.name == PROHIBITED and _allowed(msg, user):
        poll['open'] = True
        polls[msg.id] = poll
        await msg.edit(embed=_get_embed(poll))

        return

    if payload.emoji.name not in poll['options'] or not poll['open']:
        return

    await _update_poll(user, msg, payload.emoji.name, -1)
    log.info(f'{user} retracted vote for {payload.emoji} - {poll["prompt"]}')


async def on_ready():
    # clear out old polls
    now = datetime.utcnow()

    for k, p in polls.items():
        ts: datetime = p['timestamp']

        if (now - ts).total_seconds() >= POLL_EXPIRY:
            del polls[k]


def setup(bot_: Bot):
    global bot

    bot = bot_

    # settings
    register('poll.createroles', None, lambda _: True, False,
             'Roles allowed to create polls. Defaults to anyone.',
             filter=create_filter)
    register('poll.voteroles', None, lambda _: True, False,
             'Roles allowed to vote in polls. Defaults to anyone.',
             filter=vote_filter)

    # events
    bot.add_listener(on_raw_reaction_add)
    bot.add_listener(on_raw_reaction_remove)
    bot.add_listener(on_ready)

    bot.add_command(poll)


def teardown(bot: Bot):
    global settings

    for key in ('poll.createroles', 'poll.voteroles',):
        del settings[key]
