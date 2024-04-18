import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Base
from repository import populate_database

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GAME = os.getenv("GAME")

db_file = "loldle.db"
add_file = 'add_champion.json'
if not os.path.exists(db_file):
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        populate_database(session, db_file)
else:
    engine = create_engine(f"sqlite:///{db_file}")
    Session = sessionmaker(bind=engine)

if os.path.exists(add_file):
    with Session() as session:
        populate_database(session, add_file)


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix={"_"}, intents=intents)

    @property
    def session(self):
        return Session()


client = Bot()

cogs = ["Functions.guess_ability", "Functions.guess_splash", "Functions.guess_classic"]


@client.event
async def on_ready():
    print("Bot is ready")
    await client.change_presence(
        status=discord.Status.online, activity=discord.Game(GAME)
    )
    for cog in cogs:
        try:
            print(f"loading cog {cog}")
            await client.load_extension(cog)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print(f"Failed to load cog {cog}\n{exc}")


client.run(TOKEN)
