import discord
from discord.ext import commands

from models import GameState


class GuessSplash(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.game_state = GameState(bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            self.game_state.is_game_active
            and not message.author.bot
            and not message.content.startswith("_")
            and message.channel == self.game_state.thread
        ):
            if self.game_state.guess(message.content):
                await message.channel.send(
                    f"{message.author.nick if message.author.nick else message.author.display_name} guessed correct!\n"
                    f"It took {self.game_state.attempts} attempts.",
                    file=discord.File("images/splash.jpg"),
                )
                await self.game_state.stop_game()
            else:
                reply = "Wrong champion."
                self.game_state.skin.zoom_out()
                await message.channel.send(
                    reply, file=discord.File("images/edited_splash.jpg")
                )

    @commands.command()
    async def guess_splash(self, ctx):
        if not self.game_state.is_game_active:
            self.game_state.start_game()
            self.game_state.skin = self.game_state.champion.get_random_skin()
            self.game_state.skin.get_image()
            thread = await ctx.channel.create_thread(
                name="Guess Splash Art", type=discord.ChannelType.public_thread
            )
            self.game_state.thread = thread
            await thread.send(file=discord.File("images/edited_splash.jpg"))
        else:
            await ctx.send("Game is being played now!")


async def setup(bot):
    await bot.add_cog(GuessSplash(bot))
