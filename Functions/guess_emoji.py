import discord
from discord.ext import commands
from discord import app_commands

from models import GameState


class GuessEmoji(commands.Cog):
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
               )
               await self.game_state.stop_game()
               return()
            if self.game_state.guess_fuzzy(message.content):
                await message.add_reaction("⭐")
                await message.channel.send(
                    f"{message.author.nick if message.author.nick else message.author.display_name} guessed correct!\n"
                    f"It took {self.game_state.attempts} attempts.\n"
                    f"The correct answer was: {self.game_state.champion.name}\n"
                )
                await self.game_state.stop_game()
            else:
                reply = "**Wrong champion.**"
                if self.game_state.attempts == 1:
                    reply += f"\n{self.game_state.champion.emoji_1}, {self.game_state.champion.emoji_2}"
                elif self.game_state.attempts >= 2:
                    reply += f"\n{self.game_state.champion.emoji_1}, {self.game_state.champion.emoji_2}, {self.game_state.champion.emoji_3}"
                await message.channel.send(reply)

    @app_commands.command(
        name="emoji",
        description="Start a game to guess the emoji of a random champion",
    )
    async def guess_emoji(self, interaction: discord.Interaction):
        if self.game_state.is_game_active:
            await interaction.response.send_message(
                "Game is already active.", ephemeral=True
            )
            return
        await interaction.response.defer(ephemeral=True)
        self.game_state.start_game()

        thread = await interaction.channel.create_thread(
            name="Gues Emoji", type=discord.ChannelType.public_thread
        )
        self.game_state.thread = thread
        await thread.send("*Type `give_up` to give up*")
        await thread.send(self.game_state.champion.emoji_1)
        await interaction.followup.send("Game started!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(GuessEmoji(bot))
