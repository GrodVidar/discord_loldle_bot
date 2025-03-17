import discord
from discord import app_commands
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
            if message.content == "give_up":
                await message.channel.send(
                    f"You guessed {self.game_state.attempts} times.\n"
                    f"The correct answer was: {self.game_state.champion.name}\n"
                    f"The skin name is: {self.game_state.skin.name}",
                    file=discord.File("images/splash.jpg"),
                )
                await self.game_state.stop_game()
                return
            if self.game_state.guess_fuzzy(message.content):
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

    @app_commands.command(
        name="splash",
        description="Start a game to guess the splash art of a random champion",
    )
    async def guess_splash(self, interaction: discord.Interaction):
        if self.game_state.is_game_active:
            await interaction.response.send_message(
                "Game is already active.", ephemeral=True
            )
            return
        await interaction.response.defer(ephemeral=True)
        self.game_state.start_game()
        self.game_state.skin = self.game_state.champion.get_random_skin()
        self.game_state.skin.get_image()
        thread = await interaction.channel.create_thread(
            name="Guess Splash Art", type=discord.ChannelType.public_thread
        )
        self.game_state.thread = thread
        await thread.send("*Type `give_up` to give up*")
        await thread.send(file=discord.File("images/edited_splash.jpg"))
        await interaction.followup.send("Game started!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(GuessSplash(bot))
