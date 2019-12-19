import json
import re
import datetime
import random
import numpy as np
import csv
import pytz

import matplotlib.pyplot as plt
from matplotlib import style
import discord

style.use("fivethirtyeight")

with open("auth.json") as f:
    auth_dict = json.load(f)

token = auth_dict['token']
client = discord.Client()

roll_bot = "RPBot#4161"

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

def utc_to_local(utc_dt, local_tz):
    """Accepts a datetime object in UTC time, and returns the same time, in the timezone that was also passed"""
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

def get_channel_members_names(channel):
    """Returns a list of all members of a channel. If the member has a nickname, the nickname is used instead of their name, otherwise their name is used"""

    names = []
    for member in channel.members:
        if member.nick is None:
            names.append(member.name)
        else:
            names.append(member.nick)

    return names

async def get_roll_history(channel, user=None, afterDate=None):
    print("Getting roll history for", user)
    print("Roll bot is", roll_bot)

    user_rolls = []

    if afterDate is None:
        today = datetime.datetime.utcnow()
        afterDate = today - datetime.timedelta(days = 1)#yesterday by default

    # for each message in the channel
    async for message in channel.history(limit=10000, after=afterDate):
        #print(message.author,": ", message.clean_content)

        # if msg was sent by roll bot
        if str(message.author) == roll_bot:
            roll_message = re.match("@(.+)\srolled\s\*\*(\d+)\*\*.", message.clean_content, re.M|re.I)

            # roll message
            if roll_message:
                roller = roll_message.group(1)

                if roller == user or user is None:
                    roll = int(roll_message.group(2))
                    if not(roll > 100 or roll < 1):
                        #look back to see what the user rolled
                        async for prev_message in channel.history(limit=5, before=message.created_at):

                            prev_message_author = None
                            if prev_message.author.nick is None:
                                prev_message_author = prev_message.author.name
                            else:
                                prev_message_author = prev_message.author.nick

                            if user == prev_message_author and prev_message.content == "!roll 1d100":
                                #print("Found a message:", prev_message.content)
                                #print("With author:", prev_message_author)
                                
                                user_rolls.append(roll)
                                break
                    
    return user_rolls




async def parse_hist_command(command, message):
    command = command.strip()
    args = command.split()

    if len(args) == 0:
        print("no args")
        #do stuff
        return

    date = None
    user = None

    i = 0
    not_date =  True
    while i < len(args):
        # if first arg is not one of these, its a user
        # ex. *hist andtrue today
        if not(args[i] == "hour" or args[i] == "week" or args[i] == "today" or args[i] == "month" or args[i] == "year"):
            if i == 0:
                user = args[i]
            else:
                user = user + str(' ') + str(args[i])
        else:
            break

        i = i + 1

    users = get_channel_members_names(message.channel)

    if user not in users and user is not None:
        await message.channel.send("That user is not in this channel, my guy")
        return

    # set date
    if len(args) >= i+1:
        date = args[i]
    else: 
        date = "today"


    title = None
    if user is not None:
        title = str(user) + "'s Rolls - " + date.capitalize()
    else:
        title = "Party Rolls - " + date.capitalize()

    today = datetime.datetime.utcnow()

    if date == "hour":
        afterDate = today - datetime.timedelta(hours = 1)
    elif date == "today":
        afterDate = today - datetime.timedelta(days = 1)
    elif date == "week":
        afterDate = today - datetime.timedelta(weeks = 1)
    elif date == "month":
        afterDate = today - datetime.timedelta(days = today.day)
    elif date == "year":
        afterDate = today - datetime.timedelta(days = int(today.strftime("%j")))
        
    upload_message = "Rolls since " + utc_to_local(afterDate, pytz.timezone('US/Eastern')).strftime("%b %d %Y %H:%M:%S")

    await create_histogram(message, title, await get_roll_history(message.channel, user, afterDate=afterDate), upload_message, create_csv="file" in args)


@client.event
async def on_message(message):
    global roll_bot

    if message.content.startswith('*hist ') or message.content.startswith('*hist'):
        await parse_hist_command(message.content.replace('*hist ', ''), message)
        return
  
async def create_histogram(message, title, data, upload_message=None, create_csv=False):
    if len(data) < 1:
        await message.channel.send("No data to make histogram")
        return

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
            
    # File upload
    upload_file = None
    file_name = None

    # creating csv file or not
    if not create_csv:
        file_name = "hist.png"
        ax.hist(data, range=[1, 100], edgecolor='#E6E6E6', color='#EE6666')
        plt.savefig(file_name, facecolor="#36393F")

    else:
        file_name = "roll_data.csv"
        counts, bins, bars = ax.hist(data, bins=range(1, 102, 1), edgecolor='#E6E6E6', color='#EE6666')
        data_file_list = list(zip(bins, counts))
        
        #write to file
        with open(file_name, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data_file_list)


    upload_file = discord.File(file_name)

    if upload_message is None:
        upload_message = file_name

    print("Uploading file")
    await message.channel.send(upload_message, file=upload_file)
    print("File sent")


    if not create_csv:
        #print stats
        num_rolls = len(data)
        mean = np.mean(data)
        median = np.median(data)
        mode = np.bincount(data).argmax()
        mode_frequency = data.count(mode)

        info_str = title + " Stats\nRolls examined: " + str(num_rolls) + "\nMean: " + str(mean) + "\nMedian: " + str(median) + "\nMode: " + str(mode) + "\nMode frequency: " + str(mode_frequency)
        await message.channel.send("```\n" + info_str + "\n```")



client.run(token)

