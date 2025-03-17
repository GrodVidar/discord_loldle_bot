import argparse
import asyncio
import os
from typing import Optional, Literal

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Base
from repository import populate_database
from bot import Bot

parser = argparse.ArgumentParser(description="Loldle")
parser.add_argument(
    "--update",
    action="store_true",
    help="Flag to trigger update db from champion_data.json",
)
args = parser.parse_args()

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", '')
GAME = os.getenv("GAME", '')

bot = Bot(args.update, activity=discord.Game(GAME))

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
    ctx: commands.Context,
    guilds: commands.Greedy[discord.Object],
    spec: Optional[Literal["~", "*", "^"]] = None,
) -> None:
    print("sync called")
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


async def main(bot):
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main(bot))

