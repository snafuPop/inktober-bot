import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from builtins import bot
import requests
from titlecase import titlecase
import sys
import psutil
import time
from datetime import timedelta, datetime

class Info(commands.Cog):
  def __init__(self, bot):
    self.time_alive = time.time()
    self.bot = bot;


  def datetime_to_unix(self, datetime_val):
    # Because many of discord's api requests return time as a datetime object,
    # we need to manually convert it into UNIX time.
    return int(time.mktime((datetime_val).timetuple()))


  def get_uptime(self):
    # Outputs how long the bot has been active.
    uptime = timedelta(seconds = time.time() - self.time_alive)
    uptime = datetime(1,1,1) + uptime
    return "{}d {}h {}m {}s".format(uptime.day-1, uptime.hour, uptime.minute, uptime.second)


  @cog_ext.cog_slash(name = "about", description = "Pulls up information about inktober-bot.")
  async def about(self, ctx):
    # Constructing the Embed.
    embed = discord.Embed(title = "", color = self.bot.user.color)
    embed.set_author(name = "inktober-bot", url = "https://github.com/snafuPop/inktober-bot", icon_url = "https://image.flaticon.com/icons/png/512/25/25231.png")
    embed.set_thumbnail(url = self.bot.user.avatar_url)

    # Constructing additional information.
    info = []
    info.append("**Author:** {}".format(await self.bot.fetch_user(94236862280892416)))
    info.append("**Language:** Python {}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    info.append("**Discord.py Version:** {}".format(discord.__version__))
    info.append("**Host:** [PythonAnywhere](https://www.pythonanywhere.com/)")
    info.append("**Latency:** {:.4f}ms".format(self.bot.latency))
    info.append("**CPU Usage:** {}%".format(psutil.cpu_percent()))
    info.append("**Disk Usage:** {}%".format(psutil.disk_usage('/')[3]))
    info.append("**Current Uptime:** {}".format(self.get_uptime()))
    info.append("Currently supporting **{:,} servers** and **{:,} users**.".format(len(self.bot.guilds), len(self.bot.users)))

    # Adding additional fields to the Embed.
    bot_info = "\n".join(info)
    embed.add_field(name = "**__Bot Statistics__**", value = bot_info)

    # Constructing Buttons.
    buttons = [
      # Invite yvona Button.
      manage_components.create_button(
        style = ButtonStyle.URL,
        label = "Invite inktober-bot",
        url = "https://bit.ly/39Kvgxs"),
      # Github repo Button.
      manage_components.create_button(
        style = ButtonStyle.URL,
        label = "GitHub repo",
        url = "https://github.com/snafuPop/inktober-bot"),
      manage_components.create_button(
        style = ButtonStyle.URL,
        label = "Report an issue",
        url = "https://github.com/snafuPop/inktober-bot/issues/new")]
    action_row = manage_components.create_actionrow(*buttons)
    await ctx.send(embed = embed, components = [action_row])


def setup(bot):
  bot.add_cog(Info(bot))
