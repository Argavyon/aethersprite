"""
Greet extension; sends a pre-defined greeting to a specified channel when new
users join the guild.
"""

# local
from .. import log
from ..common import FakeContext, handle_member_join
from ..filters import ChannelFilter
from ..settings import register, settings

channel_filter = ChannelFilter('greet.channel')


@handle_member_join
async def member_join(member):
    "Greet members when they join."

    ctx = FakeContext(guild={'id': member.guild.id})
    chan_setting = settings['greet.channel'].get(ctx)
    msg_setting = settings['greet.message'].get(ctx)

    if chan_setting is None or msg_setting is None:
        return

    channel = [c for c in member.guild.channels if c.name == chan_setting][0]
    log.info(f'Greeting new member {member} in {member.guild} {channel}')
    await channel.send(msg_setting.format(name=member.display_name,
                                          nl='\n'))


def setup(bot):
    # settings
    register('greet.channel', None, lambda x: True, False,
             'The channel where greetings should be sent.',
             filter=channel_filter)
    register('greet.message', None, lambda x: True, False,
             'The message new members will be greeted with. You may use '
             'the `{name}` token in your message and it will be replaced '
             'automatically with the member\'s username. The `{nl}` token '
             'will be replaced with a line break (new line).')
