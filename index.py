import json
import sys
import re

import discord
import time
import spell
import my_token
import virtues_flaws
import smbonus
import baselines
import armdice

from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)

print("Ars Magica 5 Primus is alive!")
print("Started at " + time.strftime("%m/%d/%y %H:%M:%S"))

## TODO
##
## Auto-download latest version of .db

def is_basic_math_expression(string):
    pattern = r'^[-+]?(\d+(\.\d*)?|\.\d+)([+-/*]\d+(\.\d*)?)*$'
    return bool(re.match(pattern, string))

def split_string_by_n(text, n):
  """Splits a string into n parts, prioritizing spaces as breaking points.

  Args:
    text: The input string.
    n: The number of parts to split the string into.

  Returns:
    A list of n parts.
  """

  words = text.split(" ")
  part_size = len(words) // n
  parts = []

  start_index = 0
  for i in range(1, n+1):
    end_index = start_index + part_size
    part = ' '.join(words[start_index:end_index])
    parts.append(part)
    start_index = end_index

  # Handle the last part, which might have fewer words
  if len(words) % n != 0:
    last_part = ' '.join(words[start_index:])
    parts.append(last_part)

  return parts

def break_string(text):
    return split_string_by_n(text, round(len(text) / 1950)+1)
    

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send("Make Ars Magica rolls and information with slash commands like /simple 10 or /stress 15 3.")
        break

@bot.tree.command(name='size', description='Get the base size of an Individual of a form.')
@app_commands.describe(form = "The form, like Ig or Corpus.")
async def sz(interaction: discord.Interaction, form:str=''):
    await interaction.response.send_message(spell.get_spell_base_size(form))

@bot.tree.command(name='durations', description='Get a list of all Durations.')
async def dur(interaction: discord.Interaction):
    await interaction.response.send_message(spell.get_durations())

@bot.tree.command(name='ranges', description='Get a list of all Ranges.')
async def ran(interaction: discord.Interaction):
    await interaction.response.send_message(spell.get_ranges())

@bot.tree.command(name='targets', description='Get a list of all Targets.')
async def tar(interaction: discord.Interaction):
    await interaction.response.send_message(spell.get_targets())

@bot.command(name='spell', help="!spell <quoted spell name>")
async def spellquery2(ctx, *, query:str=''):    
    for s in break_string(spell.search_spell(query)):
        await ctx.send(s)        
    username = str(ctx.author.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " searche the spell " + query)

@bot.tree.command(name='spell', description='Search for a spell.')
@app_commands.describe(query = "The partial or complete name of the spell")
async def spellquery(interaction: discord.Interaction, query:str=''):    
    for index, s in enumerate(break_string(spell.search_spell(query))):
        if index == 0:
            await interaction.response.send_message(s)
        else:
            await interaction.followup.send(s)
    username = str(interaction.user.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " searche the spell " + query)

@bot.tree.command(name='virtue', description='Search for a virtue.')
@app_commands.describe(query = "The partial or complete name of the virtue")
async def virtue(interaction: discord.Interaction, query:str=''):
    for index, s in enumerate(break_string(virtues_flaws.search_virtue(query))):
        if index == 0:
            await interaction.response.send_message(s)
        else:
            await interaction.followup.send(s)    

@bot.tree.command(name='flaw', description='Search for a flaw.')
@app_commands.describe(query = "The partial or complete name of the flaw")
async def flaw(interaction: discord.Interaction, query:str=''):    
    for index, s in enumerate(break_string(virtues_flaws.search_flaw(query))):
        if index == 0:
            await interaction.response.send_message(s)
        else:
            await interaction.followup.send(s)

@bot.tree.command(name='smname', description='Search for a Shape or Material bonus.')
@app_commands.describe(query = "The partial or complete name of the Shape or Material.")
async def shapematerialname(interaction: discord.Interaction, query:str=''):
    await interaction.response.send_message(smbonus.search_sm_name(query))

@bot.tree.command(name='smbonus', description='Search for a Shape or Material by the bonus it gives.')
@app_commands.describe(query = "The partial or complete name of the bonus.")
async def shapematerialbonus(interaction: discord.Interaction, query:str=''):
    await interaction.response.send_message(smbonus.search_sm_bonus(query))

@bot.tree.command(name='guidelines', description='Get the spell guidelines for an specific technique and form.')
@app_commands.describe(tech = "The technique, like In or Rego.", form = "The form, like An or Corpus.", level="The maximum level (optional)")
async def base(interaction: discord.Interaction, tech:str='', form:str='', level:int=1000):
    for index, s in enumerate(break_string(baselines.get_baseline(tech, form, level))):
        if index == 0:
            await interaction.response.send_message(s)
        else:
            await interaction.followup.send(s)
    username = str(interaction.user.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " checked guidelines for " + tech + " " + form + " up to level " + str(level))     

@bot.command(name='guidelines', help="!guidelines <technique> <form> <level> - Check the guidelines for the Tech+Form up to level")
async def guide(ctx, tech:str, form:str, level:int=1000):
    for s in break_string(baselines.get_baseline(tech, form, level)):
        await ctx.send(s)
    username = str(ctx.author.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " checked guidelines for " + tech + " " + form + " up to level " + str(level))     

@bot.tree.command(name='simple', description='Rolls a simple dice with a modifier.')
@app_commands.describe(modifier = "The static value to modify the roll", reason = "The reason for the roll", rolltype = "Type of roll [skill|spell]", ease = "Target Number (Ease Factor)")
async def simple(interaction: discord.Interaction, modifier:int=0, rolltype:str='', ease:int=0, reason:str=''):
    username = str(interaction.user.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " rolled a simple die for " + reason)    
    await interaction.response.send_message(armdice.simple(username, modifier, rolltype, ease, reason))

@bot.tree.command(name="stress", description='Rolls a stress dice with a modifier and botch dices to roll if you roll a zero.')
@app_commands.describe(modifier = "The static value to modify the roll", botch="Numer of botch dices if you roll a zero", reason = "The reason for the roll", rolltype = "Type of roll [skill|spell]", ease = "Target Number (Ease Factor)")
async def stress(interaction: discord.Interaction, modifier: int=0, botch: int=1, rolltype:str='', ease:int=0, reason:str=''):
    username = str(interaction.user.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " rolled a stress die for " + reason)    
    await interaction.response.send_message(armdice.stress(username, modifier, botch, rolltype, ease, reason))

@bot.tree.command(name="cast", description='Rolls a stress dice with a modifier and botch dices to roll for an spontaneous cast.')
@app_commands.describe(modifier = "The static value to modify the roll", botch="Numer of botch dices if you roll a zero", reason = "The reason for the roll", magnitude = "The magnitudes added to the guideline")
async def cast(interaction: discord.Interaction, modifier: int=0, botch: int=1, magnitude: int=0, reason:str=''):
    username = str(interaction.user.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " rolled a spell for " + reason)    
    await interaction.response.send_message(armdice.cast(username, modifier, botch, magnitude, reason))

@bot.tree.command(name="roll", description='Roll traditional dice expressions.')
@app_commands.describe(diceexpression = "The dice expression, like 1d20+6", reason = "The reason for the roll")
async def roll(interaction: discord.Interaction, diceexpression: str, reason:str=''):
    username = str(interaction.user.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " rolled a dice expression " + diceexpression +  " for " + reason)    
    await interaction.response.send_message(armdice.roll(username, diceexpression, reason))

@bot.tree.command(name="age", description='Roll Aging.')
@app_commands.describe(age = "The current age of a character, like 43", modifier = "The modifiers to the aging roll, like a longevity ritual or living conditions.")
async def roll(interaction: discord.Interaction, age: int, modifier:int=0):
    username = str(interaction.user.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " rolled aging " + str(age))    
    await interaction.response.send_message(armdice.aging(username, age, modifier))

@bot.command(name='simple', help="!simple <modifier> [rolltype] [easefactor] [reason] - Rolls a simple die and add the modifier with an optional reason for the roll. Rolltype can be skill or spell.")
async def simple2(ctx, modifier:int=0, rolltype:str='', ease:int=0, reason:str=''):
    username = str(ctx.author.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " rolled a simple die for " + reason)    
    await ctx.send(armdice.simple(username, modifier, rolltype, ease, reason))

@bot.command(name='stress', help="!stress <modifier> [botch=1] [rolltype=skill|spell] [easefactor] [reason] - Rolls a stress die, add the mod. Default botches is 1. Optional reason for the roll. Rolltype can be skill or spell.")
async def stress2(ctx, modifier:int=0, botches:int=0, rolltype:str='', ease:int=0, reason:str=''):
    username = str(ctx.author.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " rolled a simple die for " + reason)    
    await ctx.send(armdice.stress(username, modifier, botches, rolltype, ease, reason))

@bot.command(name='cast', help="!spell <modifier> [botch=1] [magnitude=0] [reason] - Rolls a stress die, add the mod. Default botches is 1. Optional reason for the roll.")
async def spell2(ctx, modifier: int=0, botch: int=1, magnitude: int=0, reason:str=''):
    username = str(ctx.author.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " rolled a spell for " + reason)
    await ctx.send(armdice.cast(username, modifier, botch, magnitude, reason))

@bot.command(name='roll', help="!roll <diceexpression> [reason] - Rolls a dice expression, like 3d6. Optional reason for the roll.")
async def roll2(ctx, diceexpression: str, reason:str=''):
    username = str(ctx.author.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " rolled a dice expression: " + diceexpression + " for " + reason)    
    await ctx.send(armdice.roll(username, diceexpression, reason))

@bot.event
async def on_command_error(ctx, error):
    await ctx.send("Invalid Command - type !help for more information")
    await ctx.send(str(error))

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)
    await bot.change_presence(activity=discord.CustomActivity(name='Distilling Vis'))

bot.run(my_token.TOKEN)

