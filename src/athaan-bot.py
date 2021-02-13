import requests
import json
import discord
import asyncio
from datetime import datetime
import time

run_bot_channels = []

class AddressNotFoundException(Exception):
    pass

class InvalidChapterException(Exception):
    pass

def get_monthly_prayer_times(location, month, year):
    monthly_prayers = {}

    response = requests.get(
        "http://api.aladhan.com/v1/calendarByAddress?address={}&method=2&month={}&year={}".format(location, month, year))

    if response.status_code != 200:
        print("STATUS CODE: {} \n exiting..." .format(response.status_code))
        exit()
    else:
        data = response.json()
        for day in range(len(data['data'])):
            monthly_prayers.update({day + 1: data['data'][day]['timings']})
        return monthly_prayers

def get_time_now():
    now = datetime.now().strftime("%m/%d/%y %H:%M")
    date_time = now.split(' ')
    time = date_time[1]
    return time

def get_date_now():
    now = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    date_time = now.split(' ')
    date = date_time[0]
    return date

def get_daily_prayer_times(location, date):
    times = []
    response = requests.get(
        "http://api.aladhan.com/v1/timingsByAddress?address={}&method=2&date_or_timestamp={}".format(location, date))

    if response.status_code != 200:
        print("STATUS CODE: {} \nExiting..." .format(response.status_code))
        raise AddressNotFoundException
        return []
    else:
        data = response.json() 
        times.append(data['data']['timings']['Fajr'])
        times.append(data['data']['timings']['Dhuhr'])
        times.append(data['data']['timings']['Asr'])
        times.append(data['data']['timings']['Maghrib'])
        times.append(data['data']['timings']['Isha'])
        return times

def is_next_day():
    time = get_time_now()
    if time == '00:00' or time == '24:00':        
        return True
    return False

def create_prayer_times_table(location, date):
    daily_prayer_times = to_standard_time(get_daily_prayer_times(location, date))

    return (
    "Prayer times at {} on {}" .format(location, date) + 
    "\nFajr: " + daily_prayer_times[0] +
    "\nDhuhr: " + daily_prayer_times[1] +
    "\nAsr: " + daily_prayer_times[2] +
    "\nMaghrib: " + daily_prayer_times[3] +
    "\nIsha: " + daily_prayer_times[4]
    )

def to_standard_time(prayer_times):
    standard_times = []
    for i in prayer_times:
        hour = int(i[:2])
        minutes = i[2:]
        if hour > 12:
            hour = hour % 12
            standard_times.append(str(hour) + minutes + ' PM')
        else:
            standard_times.append(str(hour) + minutes + ' AM')
    return standard_times

def get_surah_name(chapter):
    response = requests.get(
        "http://api.alquran.cloud/v1/surah/{}".format(chapter))
    
    data = response.json()
    
    surah = data['data']['englishName']
    return surah

async def send_surah_ayahs(chapter, channel_id):
    response = requests.get(
        "http://api.alquran.cloud/v1/surah/{}".format(chapter))
    
    data = response.json()
    channel_name = client.get_channel(channel_id)
    surah = data['data']['ayahs']

    verses = []
    max_len = 50
    cur_len = 0

    for ayah in surah:
        verses.append(ayah['text'] + '❁')
        print("hit")
        cur_len += len(ayah)

        if cur_len >= max_len:
            await channel_name.send(verses)
            verses = []
            cur_len = 0
    await channel_name.send(verses)

def get_manual():
    return(
        "Commands - (Note: All commands are case insensitive)" +
        "\n\n$RunBot: The channel that is sent this command will receive prayer time notifications." +
        "\n\n$StopBot: The channel that is sent this command will stop receiving prayer time notifcations."
        "\n\n$PrayerTimes: Prints a list of the prayer times for a certain address. given an address which is comma separated. \n(Ex. $PrayerTimes 123 Oak Street, Alexandria, VA)" +
        "\n\n$MakeTakfir: Requires a name or @ paramater. Will send a message that the given paramater has left the fold of Islam." +
        "\n\n$Surah: Requires the surah number(1-114) as a parameter. Be careful with larger surahs as it will send as multiple messages and can spam chats. \n(Ex. $Surah 114)"
        "\n\nTakbir / Takbeer: Bot will respond saying Allahu Akbar."
    )

#NOTE: Run_bot only checks and sends messages to all channels based on one location, determined by variable location
async def run_bot():
    location = "4313 Mission Court, Alexandria, VA"
    today = get_date_now()
    daily_prayer_times = get_daily_prayer_times(location, today)

    while True:
        if not run_bot_channels:
            # print('NO CHANNELS')
            await asyncio.sleep(10.0)
            continue
        
        time_now = get_time_now()
        # await client.get_channel('800046347016863757').send("Time: " + time_now)
        # await client.get_channel('800046347016863757').send(run_bot_channels)

        if is_next_day():
            today = get_date_now()
            daily_prayer_times = get_daily_prayer_times(location, today)

        # For testing purposes only:
        # daily_prayer_times = ['07:55', '07:56', '07:57', '07:58', '07:52']

        for i in range(len(daily_prayer_times)):
            if time_now == daily_prayer_times[i]:
                print("Sending prayer notification to channels!")
                if i == 0:
                    for channel in run_bot_channels:
                        bot_channel = client.get_channel(channel)
                        await bot_channel.send('Wake Up - It\'s Fajr Time!')
                elif i == 1:
                    for channel in run_bot_channels:
                        bot_channel = client.get_channel(channel)
                        await bot_channel.send('Take a Break - It\'s Dhuhr Time!')
                elif i == 2:
                    for channel in run_bot_channels:
                        bot_channel = client.get_channel(channel)
                        await bot_channel.send('Make Wudhu - It\'s Asr Time!')
                elif i == 3:
                    for channel in run_bot_channels:
                        bot_channel = client.get_channel(channel)
                        await bot_channel.send('Gather For Prayer - It\'s Maghrib Time!')
                else:
                    for channel in run_bot_channels:
                        bot_channel = client.get_channel(channel)
                        await bot_channel.send('Don\'t Sleep Yet - It\'s Isha Time!')

        await asyncio.sleep(60.0)

client = discord.Client()

@client.event
async def on_ready():
    print("Log in successful! Logged in as {}" .format(client.user))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    bot_command = '$'
    location = ''

    print(message)

    if message.content.startswith(bot_command):
        content = message.content.split(' ')
        command = content[0].lower()
    
        if command == '$runbot':
            run_bot_channels.append(message.channel.id)
            await message.channel.send("This channel will now receive prayer time notifications!")

        if command == '$stopbot':
            run_bot_channels.remove(message.channel.id)
            await message.channel.send("This channel will not receive prayer time notifications.")

        if command == '$info':
            await message.channel.send(get_manual())

        if command == '$prayertimes':
            if len(content) == 1:
                await message.channel.send("Please provide an address. For more information, use command $info")
        
            else:
                content.pop(0)
                location = ' '.join(content)
                try:
                    prayer_times_table = create_prayer_times_table(location, get_date_now())
                    await message.channel.send(prayer_times_table)
                except Exception as e:
                    print(e)
                    await message.channel.send("The address you have provided could not be found. For more information on the $PrayerTimes command, use command $info")

        # can be any string name or it can be the @
        if command == '$maketakfir':
            if len(content) < 2:
                await message.channel.send('Please provide the name or @ of the person you want to make takfir on')
            else:
                await message.channel.send("{} has left the fold of Islam" .format(content[1]))

        if command == '$surah':
            if len(content) < 2 or int(content[1]) < 1 or int(content[1]) > 114 :
                await message.channel.send("Please provide a surah number from 1-114. For more information, use command $info")

            try:
                await message.channel.send(get_surah_name(content[1]))
                await send_surah_ayahs(content[1], message.channel.id)

            except Exception as e:
                "Surah could not be found. Please provide the surah number as a parameter. For more information, use the command $info"

    if message.content.lower() == 'takbeer' or message.content.lower() == 'takbir':
        await message.channel.send('الله أكبر')

asyncio.get_event_loop().create_task(run_bot())

client.run('Nzk5Njc1NDcwMzAzODU0NjAy.YAHB0Q.kWwPML4tJOX8wOpK80kIec4eqSs')
