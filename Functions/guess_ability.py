import discord
from discord.ext import commands
from discord import app_commands

from models import GameState


class GuessAbility(commands.Cog):
    FIRST_HINT = 5
    SECOND_HINT = 10
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
                    f"The ability name is: {self.game_state.ability.name}",
                    file=discord.File("images/ability.png"),
                )
                await self.game_state.stop_game()
                return
            if self.game_state.guess_fuzzy(message.content):
                await message.channel.send(
                    f"{message.author.nick if message.author.nick else message.author.display_name} guessed correct!\n"
                    f"It took {self.game_state.attempts} attempts.",
                )
                await self.game_state.stop_game()
            else:
                reply = "Wrong champion.\n"
                if self.game_state.attempts < 5:
                    reply += f"{5 - self.game_state.attempts} left to get ability name"
                else:
                    reply += "Type `_hint` to receive a hint"
                await message.channel.send(reply)

    @app_commands.command(
        name="ability",
        description="Start a game to guess the ability icon of a random champion",
    )
    async def guess_ability(self, interaction: discord.Interaction):
        if self.game_state.is_game_active:
            await interaction.response.send_message(
                "Game is already active.", ephemeral=True
            )
            return
        await interaction.response.defer(ephemeral=True)
        self.game_state.start_game()
        self.game_state.ability = self.game_state.champion.get_random_ability()

        self.game_state.ability.get_image()
        thread = await interaction.channel.create_thread(
            name="Guess Ability", type=discord.ChannelType.public_thread
        )
        self.game_state.thread = thread
        await thread.send("*Type `give_up` to give up*")
        await thread.send(file=discord.File("images/edited_ability.png"))
        await interaction.followup.send("Game started!", ephemeral=True)

    @app_commands.command(
        name="hint",
        description=f"Get a hint for the ability name, hints are available after {FIRST_HINT} attempts",
    )
    async def hint(self, interaction: discord.Interaction):
        if not self.game_state.is_game_active:
            return await interaction.response.send_message(
                "No active game", ephemeral=True
            )
        if interaction.channel != self.game_state.thread:
            return await interaction.response.send_message(
                "You can only get hints in the game thread", ephemeral=True
            )
        if self.game_state.attempts < self.FIRST_HINT:
            return await interaction.response.send_message(
                f"You need to guess at least {self.FIRST_HINT} times to get a hint, {self.FIRST_HINT - self.game_state.attempts} guesses left.", ephemeral=True
            )

        if self.FIRST_HINT <= self.game_state.attempts < self.SECOND_HINT:
            await interaction.followup.send(
                f"Ability name: {self.game_state.ability.name}\n"
                f"Next hint after {self.SECOND_HINT - self.game_state.attempts} attempts"
            )
        else:
            await interaction.followup.send(
                f"Ability name: {self.game_state.ability.name}",
                file=discord.File("images/ability.png"),
            )


async def setup(bot):
    await bot.add_cog(GuessAbility(bot))
