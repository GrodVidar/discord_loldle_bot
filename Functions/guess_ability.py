import discord
from discord.ext import commands

from models import GameState


class GuessAbility(commands.Cog):
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
            if message.content == 'give_up':
                await message.channel.send(f"You guessed {self.game_state.attempts} times.\n"
                                           f"The correct answer was: {self.game_state.champion.name}\n"
                                           f"The ability name is: {self.game_state.ability.name}",
                                           file=discord.File("images/ability.png"))
                await self.game_state.stop_game()
                return
            if self.game_state.guess(message.content):
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

    @commands.command()
    async def guess_ability(self, ctx):
        if not self.game_state.is_game_active:
            self.game_state.start_game()
            self.game_state.ability = self.game_state.champion.get_random_ability()

            self.game_state.ability.get_image()
            thread = await ctx.channel.create_thread(
                name="Guess Ability", type=discord.ChannelType.public_thread
            )
            self.game_state.thread = thread
            await thread.send("*Type `give_up` to give up*")
            await thread.send(file=discord.File("images/edited_ability.png"))
        else:
            await ctx.send("Game is being played now!")

    @commands.command()
    async def hint(self, ctx):
        if ctx.channel == self.game_state.thread:
            if self.game_state.attempts < 5:
                await ctx.send(
                    f"{5 - self.game_state.attempts} Attempts left to get the next hint"
                )
            elif 5 <= self.game_state.attempts < 10:
                await ctx.send(
                    f"Ability name: {self.game_state.ability.name}\n"
                    f"Next hint after {10 - self.game_state.attempts} attempts"
                )
            else:
                await ctx.send(
                    f"Ability name: {self.game_state.ability.name}",
                    file=discord.File("images/ability.png"),
                )


async def setup(bot):
    await bot.add_cog(GuessAbility(bot))
