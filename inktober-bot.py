import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from ButtonPaginator import Paginator
from builtins import bot, guild_ids
import random
import math
import json
import os
from titlecase import titlecase
import datetime
import requests

class Inktober(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


# --------------------------------------------------------------------
# helper commands
# --------------------------------------------------------------------

  def get_data_path(self):
    # returns the filepath of the _data folder
    return os.path.dirname(__file__) + "/_data/"


  def get_words(self):
    # returns the list of stored words as a set
    filepath = self.get_data_path()
    with open(filepath + "words.txt") as word_data:
      return set(word_data.readlines())

  def get_users(self):
    # returns the list of all registered users as a dictionary
    filepath = self.get_data_path()
    with open(filepath + "users.json") as json_data:
      return json.load(json_data)

  def update_users(self, user_dict):
    # updates the user dictionary file with argument user_dict
    filepath = self.get_data_path()
    with open(filepath + "users.json", "w") as json_out:
      json.dump(user_dict, json_out, indent = 2)


  def is_october(self):
    # check if it's october
    print(datetime.datetime.now().strftime("%m"))
    return datetime.datetime.now().strftime("%m") == "10"


  def convert_words_into_list(self, word_string):
    # separates a single string of word(s) into a set
    # separates them on comma and leading spaces, then titlecases them
    words = word_string.split(",")
    for i in range(len(words)):
      words[i] = titlecase(words[i].lstrip(' '))
    return set(words)


  def pick_words(self):
    # generates a list of 31 unique words from the wordbank 
    words = list(self.get_words())
    word_list = [None] * 31
    for i in range(len(word_list)):
      popped_word = random.choice(words)
      words.remove(popped_word)
      word_list[i] = popped_word[:-1]
    return word_list


  def check_if_image_url(self, image_url):
    # checks if a given image url is valid
   image_formats = ("image/png", "image/jpeg", "image/jpg")
   r = requests.head(image_url)
   return r.headers["content-type"] in image_formats


# --------------------------------------------------------------------
# owner commands
# --------------------------------------------------------------------


# --------------------------------------------------------------------
# slash commands
# --------------------------------------------------------------------

  @cog_ext.cog_slash(name = "word", description = "Submits a word into the Inktober word bank for the current year.", 
    options = [create_option(
      name = "word",
      description = "The word to be added. Multiple words can be added by separating each with a comma (\",\").",
      option_type = 3,
      required = True)])
  async def submit_word(self, ctx, word: str = None):
    # takes in word(s) from the user and adds them to the word database
    # words that are already in the database are ignored

    words = self.convert_words_into_list(word)
    word_database = self.get_words()
    already_exists = set()
    word_counter = 0

    with open(self.get_data_path() + "words.txt", "a") as word_file:
      for word in words:
        if word in word_database:
          already_exists.add(word)
          print("Did not add {}".format(word))
        else:
          word_file.write("\n" + word)
          print("Added {}".format(word))
          word_counter += 1

    if word_counter > 0:
      embed = discord.Embed(title = "", description = ":white_check_mark: **{:,}** word(s) have been added.".format(word_counter))
      if len(already_exists) > 0:
        embed.add_field(name = "**Warning:**", value = ":warning: **{:,}** word(s) have been ignored since they are already in the word list:\n{}".format(len(already_exists), str(already_exists)))
    else:
      embed = discord.Embed(title = "", description = ":no_entry: This/These words are already on the word list. No words have been added:\n{}".format(str(already_exists)))
    await ctx.send(embed = embed)



  @cog_ext.cog_slash(name = "register", description = "Registers yourself as a participant for Inktober and generates a word for each day.")
  async def register(self, ctx):
    user_dict = self.get_users()
    if str(ctx.author.id) in user_dict:
      embed = discord.Embed(title = "", description = ":no_entry: You're already reigstered!")
      await ctx.send(embed = embed)
      return

    user_dict[str(ctx.author.id)] = {"words": self.pick_words(), "images": [None] * 31}
    self.update_users(user_dict)
    embed = discord.Embed(title = "Success!", description = "You have been registered as a participant for Inktober, and 31 words have been assigned to you. You can check your daily word by using `/daily`.")
    await ctx.send(embed = embed)



  @cog_ext.cog_slash(name = "daily", description = "Checks your word of the day.", guild_ids = guild_ids)
  async def daily(self, ctx):
    if str(ctx.author.id) not in self.get_users():
      embed = discord.Embed(title = "", description = ":no_entry: You're not reigstered! You `/register` to register yourself as a participant.")
      await ctx.send(embed = embed)
      return

    if not self.is_october():
      embed = discord.Embed(title = "", description = ":no_entry: It's not October!")
      await ctx.send(embed = embed)
      return

    day_number = datetime.datetime.today().day
    daily_word = self.get_users()[str(ctx.author.id)]["words"][day_number]

    now = datetime.datetime.now()
    time_left = ((24 - now.hour - 1) * 60 * 60) + ((60 - now.minute - 1) * 60) + (60 - now.second)
    hours = time_left // 3600
    minutes = time_left % 3600 // 60
    seconds = time_left % 60

    embed = discord.Embed(title = "", description = "🗓️ Your word for October {} is **{}**.".format(day_number, daily_word), color = ctx.author.color)
    embed.set_author(name = "{}'s Word of the Day:".format(ctx.author.name), icon_url = ctx.author.avatar_url)
    embed.set_footer(text = "{}h {}m {}s until the next day (reset is midnight EST)".format(hours, minutes, seconds))

    await ctx.send(embed = embed)



  @cog_ext.cog_slash(name = "portfolio", description = "Pulls up a user's portfolio (leave no arguments to get your own portfolio).",
    options = [create_option(
      name = "user",
      description = "The name of a user.",
      option_type = 6,
      required = False)])
  async def portfolio(self, ctx, user: discord.Member = None):
    await ctx.defer()
    if user is None:
      user = ctx.author

    user_dict = self.get_users()

    if (ctx.author == user) and (str(user.id) not in user_dict):
      embed = discord.Embed(title = "", description = ":no_entry: You're not reigstered! You `/register` to register yourself as a participant.")
      await ctx.send(embed = embed)
      return

    if (str(user.id) not in user_dict):
      embed = discord.Embed(title = "", description = ":no_entry: {} isn't reigstered!".format(user.name))
      await ctx.send(embed = embed)
      return

    user_profile = user_dict[str(user.id)]
    images = user_profile["images"]
    words = user_profile["words"]
    embeds = []
    for i in range(30, -1, -1):
      if images[i] is not None:
        embed = discord.Embed(title = "🗓️ **October {}:** *{}*".format(i + 1, words[i]))
        embed.set_author(name = "{}'s Portfolio".format(user.name), icon_url = user.avatar_url)
        embed.set_image(url = images[i])
        embeds.append(embed)

    if len(embeds) == 0:
      embed = discord.Embed(title = "", description = "{} hasn't uploaded any images yet!".format(user.name))
      await ctx.send(embed = embed)
      return

    paginated_embed = Paginator(bot = self.bot, ctx = ctx, embeds = embeds, only = ctx.author)
    await paginated_embed.start()



  @cog_ext.cog_slash(name = "upload", description = "Uploads an image for today's date (or specific date if specified).",
    options = [create_option(
      name = "url",
      description = "URL of the image to be uploaded.",
      option_type = 3,
      required = True),
    create_option(
      name = "day",
      description = "Day number.",
      option_type = 4,
      required = False)])
  async def upload(self, ctx, url: str = None, day: int = datetime.datetime.today().day):
    user_dict = self.get_users()

    if str(ctx.author.id) not in user_dict:
      embed = discord.Embed(title = "", description = ":no_entry: You're not reigstered! You `/register` to register yourself as a participant.")
      await ctx.send(embed = embed)
      return

    if not self.is_october():
      embed = discord.Embed(title = "", description = ":no_entry: It's not October!")
      await ctx.send(embed = embed)
      return

    if not self.check_if_image_url(url):
      embed = discord.Embed(title = "", description = ":no_entry: Not a valid image URL (Image must be of `.png`, `.jpeg`, or `.jpg`).")
      await ctx.send(embed = embed)
      return

    user_dict[str(ctx.author.id)]["images"][day-1] = url
    self.update_users(user_dict)

    embed = discord.Embed(title = "", description = ":white_check_mark: Successfully uploaded image for October {}!".format(day))
    await ctx.send(embed = embed)


def setup(bot):
  bot.add_cog(Inktober(bot))
