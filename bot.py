import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from repository import populate_database
from models import Base

EXTENSIONS = [
    "Functions.guess_ability",
    "Functions.guess_splash",
    "Functions.guess_classic",
]


class Bot(commands.Bot):

    def __init__(self, update=False, *args, **kwargs):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        db_file = "loldle.db"
        db_exists = os.path.exists(db_file)
        engine = create_engine(f'sqlite:///{db_file}')
        self.Session = sessionmaker(bind=engine)

        if not db_exists:
            Base.metadata.create_all(engine)
            with self.Session() as session:
                populate_database(session, 'champion_data.json')
        else:
            if update and os.path.exists('add_champion.json'):
                with self.Session() as session:
                    populate_database(session, 'add_champion.json')
                    os.remove('add_champion.json')

        super().__init__(command_prefix={"_"}, intents=intents)

    @property
    def session(self):
        return self.Session()

    async def on_ready(self):
        await self.tree.sync()

    async def setup_hook(self) -> None:
        for extension in EXTENSIONS:
            await self.load_extension(extension)
            print("Added extension: ", extension)
        return await super().setup_hook()
