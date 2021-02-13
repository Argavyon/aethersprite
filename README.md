# ncfacbot

A [Nexus Clash] Faction [Discord] bot.

<img src="https://raw.githubusercontent.com/haliphax/ncfacbot/assets/assets/ncfacbot-header.jpg" style="width: 100%; max-width: 100%;" alt="Header image" />

_This bot is a work in progress. Please excuse my mess..._

## Features

- Multi-server, multi-channel capable
- Built on [discord.py], so new commands are easy to create and integrate
- Server- and channel-specific settings framework for command customization
  - Input and output filters for further customization of settings
- Role-based authorization for commands
- Persistence of data and scheduled events during downtime
- [Flask]-based web application for web hooks, pages, file storage, etc.
- Deal with friendly role and channel names in commands, but store reliable
  IDs for permanence

## Commands

- `alias`
  Manage aliases for other commands
- `closest`
  Return the closest tick to the given GMT offset (or now)
- `github`
  Information about the project and a link to this repository
- `gmt`
  Get the current time (or an offset from now) in GMT
- `lobotomy`
  A collection of commands for enabling/disabling other commands per-server
  and per-channel
- `nick`
  Change the bot's nickname per-server
- `only`
  Only allow whitelisted commands in a channel
- `raid`
  A collection of commands for scheduling and announcing raids
- `safe`
  A collection of commands for viewing faction safe contents -
  [Discord Bot Safe README]
- `settings`
  A collection of commands for manipulating the bot's settings framework
- `shop`
  A collection of commands for viewing and maintaining crafting/alchemy/ammo
  shopping lists
- `sm`
  Announce the end of Sorcerers Might
- `tick`
  GMT timestamp and timespan (e.g. _"1 day, 8 hours, 4 minutes"_) of the next
  tick (or _x_ ticks from now)

## Stand-alone settings

Some of the settings in the project do not have corresponding commands, and
operate based entirely on events.

- `greet.channel` _(server)_
  The channel where greeting messages should be sent. Defaults to an empty
  value. Both the channel and message must be set before this feature will be
  enabled.
- `greet.message` _(server)_
  The message that will be used to greet new users when they join the server.
  If set to the default, no greeting will be posted. You may use the `{name}`
  token in your message, and it will be replaced with the new member's
  username.
- `nameonly` _(server)_
  If set to anything other than the default value, the bot will only respond
  if it is mentioned directly
- `nameonly.channel` _(channel)_
  Like `nameonly`, but this setting applies to individual channels

## Plans

- Ability to set guild for using guild-locked commands via DM
- Set command prefix per-server and per-channel
- Split bot framework into separate project, leave NC commands here
- [TOML] configuration file(s) for immutable settings

## Pipe dreams

- Tie-in with TamperMonkey UserScript for aggregating search odds data
- ...


[discord.py]: https://discordpy.readthedocs.io
[Discord]: https://discordapp.com
[Discord Bot Safe README]: ./ncfacbot/extensions/safe.md
[Flask]: https://flask.palletsprojects.com
[Nexus Clash]: https://www.nexusclash.com
[TOML]: https://github.com/toml-lang/toml
