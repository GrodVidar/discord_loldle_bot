from models import Champion
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
GAME = os.getenv('GAME')


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

cogs = ['Functions.guess_ability', 'Functions.guess_splash']

client = commands.Bot(command_prefix='_', help_command=None, intents=intents)


@client.event
async def on_ready():
    print("Bot is ready")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(GAME))
    for cog in cogs:
        try:
            print(f"loading cog {cog}")
            await client.load_extension(cog)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print(f"Failed to load cog {cog}\n{exc}")


client.run(TOKEN)
