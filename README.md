"# prayer_time_bot_discord_py" 

This is a discord bot that uses the discord.py API. The main functionality of this bot is to send prayer time alerts to discord channels whenever it's a prayer time. 
This bot is continuously running in order to check if it is a prayer time every minute. However, using the asyncio module, the bot is constantly listening for events and
responding appropriately. In order for a channel to receive prayer time notifications, the bot must be in the server and the function '$runbot" must be run in the channel that wishes to recieve these notifications. This bot uses the http://api.aladhan.com/ rest API to retrieve daily prayer times every day at midnight. 

Other bot functions / Bot command Manual:

Commands - (Note: All commands are case insensitive)

$RunBot: The channel that is sent this command will receive prayer time notifications.

$StopBot: The channel that is sent this command will stop receiving prayer time notifcations.

$PrayerTimes: Prints a list of the prayer times for a certain address. given an address which is comma separated. 
(Ex. $PrayerTimes 123 Oak Street, Alexandria, VA)

$MakeTakfir: Requires a name or @ paramater. Will send a message that the given paramater has left the fold of Islam.

$Surah: Requires the surah number(1-114) as a parameter. Be careful with larger surahs as it will send as multiple messages and can spam chats. Uses the http://api.alquran.cloud/v1/surah/ API
(Ex. $Surah 114)

Takbir / Takbeer: Bot will respond saying Allahu Akbar.
