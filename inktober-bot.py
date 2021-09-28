from os.path import dirname, basename, isfile
import sys
import glob
import os
import builtins
import importlib
import inspect
from enum import Enum
import json
from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext
from discord.ext.commands import Bot

# attempt to import discord.py
try:
  import discord
  from discord.ext import commands
except ImportError:
  print("discord.py was not found.")
  sys.exit(1)

# getting directory information
dirname = os.path.dirname(__file__)
settings_file_path = os.path.join(dirname, '_config/settings.json')
modules_path = os.path.join(dirname, 'modules/')

# opening initial settings
def get_config():
  with open(settings_file_path) as json_data:
    return json.load(json_data)

def update_config(config):
  with open(settings_file_path) as json_out:
    json.dump(config, json_out, indent = 2)

def get_prefix(bot, ctx):
  try:
    guild = str(ctx.guild.id)
  except:
    return ""
  prefixes = get_config()["PREFIXES"]
  return prefixes.get(guild, "yv ")

# load intents
intents = Intents.default()

# load the token, prefixes, and intents
TOKEN = get_config()["TOKEN"]
#bot = commands.Bot(command_prefix = get_prefix, intents = intents)
bot = Bot(command_prefix = get_prefix, self_bot = True, help_command = None, intents = intents)
slash = SlashCommand(bot, sync_commands = True)
guild_ids = [482725089217871893]
builtins.bot = bot
builtins.guild_ids = guild_ids
#bot.remove_command('help')

# imports
successful_imports = 0
total_imports = 0
print("\n")
for file in os.listdir(modules_path):
  filename = os.fsdecode(file)
  if filename != "__init__.py" and filename.endswith(".py"):
    total_imports += 1
    try:
      bot.load_extension("modules." + filename[:-3])
      print("{} was loaded successfully!".format(filename), flush = True)
      successful_imports += 1
    except Exception as e:
      print("{} had some problems ({}: {})".format(filename, type(e).__name__, e), flush = True)

@bot.event
async def on_ready():
  # runs when the bot is fully functional
  print("\n{}/{} modules loaded".format(successful_imports, total_imports), flush = True)
  print("Logged in as {} <{}>".format(bot.user.name, bot.user.id), flush = True)
  print("Running {}".format(discord.__version__), flush = True)
  print("--------------------------------------------------------", flush = True)


bot.run(TOKEN)