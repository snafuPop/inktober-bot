import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from builtins import bot, guild_ids
import random
import math
import json
import os
from titlecase import titlecase

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
    return set(open(filepath + "words.txt").read().split())


  def get_users(self):
    # returns the list of all registered users as a dictionary
    filepath = self.get_data_path()
    with open(filepath + "users.json") as json_data:
      return json.load(json_data)


  def convert_words_into_list(self, word_string):
    # separates a single string of word(s) into a set
    # separates them on comma and leading spaces, then titlecases them
    words = word_string.split(",")
    for i in range(len(words)):
      words[i] = titlecase(words[i].lstrip(' '))
    return set(words)



# --------------------------------------------------------------------
# owner commands
# --------------------------------------------------------------------


# --------------------------------------------------------------------
# word commands
# --------------------------------------------------------------------

  @cog_ext.cog_slash(name = "word", description = "Submits a word into the Inktober word bank for the current year.", guild_ids = guild_ids, 
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
    already_exists = {}
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
      embed = discord.Embed(title = "**Successfully added to the word list.**", description = "**{:,}** words have been added.".format(word_counter))
      if len(already_exists) > 0:
        embed.add_field(name = "**{:,}** word(s) have been ignored since they are already in the word list.".format(len(already_exists)), value = str(already_exists))
    else:
      embed = discord.Embed(title = "**Error:**", description = "This/These words are already on the word list. No words have been added.")
    await ctx.send(embed = embed)




# --------------------------------------------------------------------
# registration commands
# --------------------------------------------------------------------



def setup(bot):
  bot.add_cog(Inktober(bot))
