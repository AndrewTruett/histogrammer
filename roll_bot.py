import json
import random
import re
import discord
import numpy as np

from Roll import Roll
from Roller import Roller


with open("auth.json") as f:
    auth_dict = json.load(f)

token = auth_dict['token']
client = discord.Client()

rollers = np.array([])

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    # load up users from file
    # ...

    # for testing

def get_user_nick(user):
    """Returns the nickname of the passed user, the name otherwise"""
    if user.nick is None:
        return user.name
    return user.nick

@client.event
async def on_message(message):
    
    if message.content.startswith('*roll ') or message.content.startswith('*roll'):
        await parse_roll_command(message.content.replace('*roll ', ''), message)
        return

async def parse_roll_command(command, message):
    command = command.strip()
    args = command.split()

    if len(args) != 1:
        await message.channel.send("@" + str(get_user_nick(message.author)) + "Invalid dice expression")
        return


    dice_expression = args[0]
    # want args to be something like 1d100
    
    tokens = dice_expression.split("d")
    if tokens[0] == dice_expression:
        await message.channel.send("@" + str(get_user_nick(message.author)) + " Invalid dice expression")
        return

    if len(tokens) != 2:
        await message.channel.send("@" + str(get_user_nick(message.author)) + " Invalid dice expression")
        return

    quantity = int(tokens[0])
    dice = int(tokens[1])

    try:
        roll = Roll(quantity, dice, message.author, message.created_at)
    except ValueError as e:
        print(e)
        return 

    # we know it was a valid roll command - save the user that rolled
    global rollers

    # if we didnt already have them, add them
    if message.author not in rollers:
        rollers = np.append(rollers, Roller(message.author))
    
    # find the user that rolled
    roller_user_names = []

    for roller in rollers:
        roller_user_names.append(get_user_nick(roller.user))

    roller = np.where(roller_user_names == get_user_nick(message.author))

    print(roller_user_names.index(get_user_nick(message.author)))
    print(roller_user_names)
    print(get_user_nick(message.author))
    print(roller)

    
    if len(roll.rolls) == 1:
        await message.channel.send("@" + str(get_user_nick(message.author)) + " rolled " + str(roll) + ".")
    else:
        add_message = "("
        i = 0
        while i < len(roll.rolls):
            add_message = add_message + str(roll.rolls[i])

            if i != len(roll.rolls)-1:
                add_message = add_message + " + "
            i = i+1

        add_message = add_message + " = " + str(roll) + ")"
        await message.channel.send("@" + str(get_user_nick(message.author)) + " rolled " + str(roll) + ". " + add_message)


client.run(token)

    