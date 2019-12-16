import json
import re
import time
import random
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import style
import discord

style.use("fivethirtyeight")

with open("auth.json") as f:
    auth_dict = json.load(f)

token = auth_dict['token']
client = discord.Client()

roll_bot = "andtrue#2032"#"RPBot#4161"

rolls = []

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    global rolls
    roll = random.randint(1, 100)
    rolls.append(roll)

    # change roll bot
    new_roll_bot = re.match("^\*set roll bot (.+)", message.content, re.M|re.I)
    if new_roll_bot:
        roll_bot = new_roll_bot.group(1)

    # user histogram - no limit
    user_histogram = re.match("^\*hist (.+)$", message.content, re.M|re.I)

    # user histogram limit
    user_histogram_limit = re.match("^\*hist (.+) (\d+)$", message.content, re.M|re.I)

    if user_histogram_limit:
        user = user_histogram_limit.group(1)
        
        limit = int(user_histogram_limit.group(2))

        users = (u.name for u in message.channel.members)
        print(users)
        if user in users:
            title = str(user) + "'s Rolls"
            await create_histogram(message, title, await get_roll_history(message.channel, user, limit))
        else:
            await message.channel.send("That user is not in this channel")

    elif user_histogram:
        user = user_histogram.group(1)
        
        users = (u.name for u in message.channel.members)
        print(users)
        if user in users:
            title = str(user) + "'s Rolls"
            await create_histogram(message, title, await get_roll_history(message.channel, user))
        else:
            await message.channel.send("That user is not in this channel, my guy")

    
    

    # clear rolls this session
    if message.content == "*clear":
        print("Clearing...")
        rolls = []
    
    # show histogram of current session
    if message.content == "*hist":
        await create_histogram(message, "Party Rolls", rolls)


    
    match = re.match("@.+\\srolled\\s(\\d+).", message.content, re.M|re.I)
    roll = -1
    if match:
        roll = int(match.group(1))
        rolls.append(roll)

        await message.channel.send(roll)
     

async def create_histogram(message, title, data):
    print("Creating histogram...")
    plt.clf()

    ax = plt.axes()

    plt.title(title)
    ax.title.set_color('dimgrey')
        
    ax.set_axisbelow(True)

    # grid lines
    plt.grid(color='dimgrey', linestyle='solid')

    # grid background
    ax.set_facecolor("#36393F")

    # hide axis spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # tick frequency    
        

    # hide top and right ticks
    ax.xaxis.tick_bottom()
    ax.yaxis.tick_left()

    # lighten ticks and labels
    ax.tick_params(colors='dimgrey', direction='out')
    for tick in ax.get_xticklabels():
        tick.set_color('dimgrey')
    for tick in ax.get_yticklabels():
        tick.set_color('dimgrey')
            
    # control face and edge color of histogram
    n, bins, patches = ax.hist(data, range=[1, 100], edgecolor='#E6E6E6', color='#EE6666')

    maxfreq = n.max()

    # set a clean upper y-axis limit
    plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)

    plt.savefig("hist.png", facecolor="#36393F")
    print("Saved...")
    print("Uploading file")

    file = discord.File("hist.png")
    await message.channel.send("hist.png", file=file)
    print("File sent")

    info_str = str(message.author) + " Stats\nRolls examined: " + str(len(data)) + "\nMean: " + str(np.mean(data)) + "\nMedian: " + str(np.median(data)) + "\nMost common: " + str(np.bincount(data).argmax()) + "\nMost common frequency: " + str(maxfreq)
    await message.channel.send("```\n" + info_str + "\n```")

async def get_roll_history(channel, user, limit=100):
    print("Getting roll history for", user)
    print("Roll bot is", roll_bot)

    user_rolls = []
    # for each message in the channel
    async for message in channel.history(limit=limit):
        #print(message.author,": ", message.content)

        # if msg was sent by roll bot
        if str(message.author) == roll_bot:
            roll_message = re.match("@(.+)\\srolled\\s(\\d+).", message.clean_content, re.M|re.I)

            # roll message
            if roll_message:
                roller = roll_message.group(1)
                if roller == user:
                    roll = int(roll_message.group(2))
                    if roll > 100 or roll < 1:
                        continue
                    
                    user_rolls.append(roll)
    return user_rolls
                




client.run(token)

