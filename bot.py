import json
import re

import discord

with open("auth.json") as f:
    auth_dict = json.load(f)

token = auth_dict['token']

client = discord.Client()

rolls = []

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):

    match = re.match("@.+rolled\\s(\\d+).", message.content, re.M|re.I)
    roll = -1
    if match:
        roll = int(match.group(1))
    #if 'happy birthday' in message.content.lower():
    #    await message.channel.send('Happy Birthday! 🎈🎉')

client.run(token)

