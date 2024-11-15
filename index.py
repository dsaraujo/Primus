import json
import sys
import re

import discord
import random
import time
import spell
import virtues_flaws

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

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send("Make Ars Magica rolls and information with slash commands like /simple 10 or /stress 15 3.")
        break

@bot.tree.command(name='size', description='Get the base size of an Individual of a form.')
@app_commands.describe(form = "The form, like In or Corpus.")
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

@bot.tree.command(name='spell', description='Search for a spell.')
@app_commands.describe(query = "The partial or complete name of the spell")
async def spellquery(interaction: discord.Interaction, query:str=''):
    await interaction.response.send_message(spell.search_spell(query))

@bot.tree.command(name='virtue', description='Search for a virtue.')
@app_commands.describe(query = "The partial or complete name of the virtue")
async def virtue(interaction: discord.Interaction, query:str=''):
    await interaction.response.send_message(virtues_flaws.search_virtue(query))

@bot.tree.command(name='flaw', description='Search for a flaw.')
@app_commands.describe(query = "The partial or complete name of the flaw")
async def flaw(interaction: discord.Interaction, query:str=''):
    await interaction.response.send_message(virtues_flaws.search_flaw(query))

@bot.tree.command(name='simple', description='Rolls a simple dice with a modifier.')
@app_commands.describe(modifier = "The static value to modify the roll")
async def simple(interaction: discord.Interaction, modifier:int=0):
    username = str(interaction.user.display_name)
    print(time.strftime("%m/%d/%y %H:%M:%S") + " " + username + " rolled a simple die")
    roll = random.randint(1, 10)
    if modifier == 0:
        response = username + " rolls a simple die\n"
        response = response + "Result: " + str(roll)
    else:
        response = username + " rolls " + str(modifier) + " plus a simple die\n"
        response = response + "Result: " + str(modifier) + " + " + str(roll) + " = " + str(modifier+roll)
    await interaction.response.send_message(response)

@bot.tree.command(name="stress", description='Rolls a stress dice with a modifier and botch dices to roll if you roll a zero.')
@app_commands.describe(modifier = "The static value to modify the roll", botch="Numer of botch dices if you roll a zero")
async def stress(interaction: discord.Interaction, modifier: int=0, botch: int=1):
    print(time.strftime("%m/%d/%y %H:%M:%S") + " someone rolled a stress die")
    if modifier == 0:
        response = str(interaction.user.display_name) + " rolls a stress die"
    else:
        response = str(interaction.user.display_name) + " rolls " + str(modifier) + " plus a stress die"

    if botch == 0:
        response = response + " (no botch):\n"
    elif botch == 1:
        response = response + " (1 botch die):\n"
    else:
        response = response + " (" + str(botch) + " botch dice):\n"

    #Limit botch dice so someone doesn't crash the server with 999,999,999,999...
    if botch > 25:
        botch = 25
        response = response + "Botch dice capped at 25 to prevent server abuse.\n"

    multiplier = 1
    roll = random.randint(0, 9)
    
    if roll == 0:
        if botch == 0:
            # no botch dice, so it's just a zero
            response = response + "Result: " + str(modifier)
        elif botch > 0:
            response = response + "Rolled a 0, Checking for Botch: "
            botches = 0
            for b in range (1,botch+1):
                botchdie = random.randint(0,9)
                response = response + str(botchdie)
                if b < botch:
                    response = response + ", "
                if botchdie == 0:
                    botches = botches + 1
            response = response + "\n"
            if botches == 0:
                response = response + "Result: " + str(modifier) + " + 0 = " + str(modifier) + " (no botches - whew!)"
            elif botches == 1:
                response = response + "Result: 0 (1 botch!)"
            else:
                response = response + "Result: 0 (" + str(botches) + " botches!)"
    else:
        # a 0 was not rolled, so process the stress roll normally
        while roll == 1:
            if multiplier == 1:
                response = response + "Roll: "
            multiplier = multiplier * 2
            response = response + '1, '
            roll = random.randint(1,10)
        
        if multiplier > 1:
            response = response + str(roll)
            response = response + " (x" + str(multiplier) + ") = " + str(roll*multiplier) + "\n"
        
        if modifier == 0:
            response = response + "Result: " + str(roll * multiplier)
        else:
            response = response + "Result: " + str(modifier) + " + " + str(roll * multiplier) + " = " + str((roll*multiplier + modifier))

    await interaction.response.send_message(response)

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

bot.run('MTMwNjAwMzE0NzkzNTg0MjMwNQ.G0cFdk.WSUPlfk4mePQBI3DFEDeK-hHb4G29bpjlklnMY')

