import discord
from discord.ext import commands
from models import GameState


class GuessAbility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_state = GameState()

    is_game_active = False

    @commands.Cog.listener()
    async def on_message(self, message):
        if (self.is_game_active
                and not message.author.bot
                and not message.content.startswith('_')
                and message.channel == self.game_state.thread):
            if self.game_state.guess(message.content):
                await message.channel.send(
                    f"{message.author} Guessed correct!\nIt took {self.game_state.attempts} attempts."
                )
                self.game_state.stop_game()
                self.is_game_active = False
            else:
                reply = "Wrong champion.\n"
                if self.game_state.attempts < 5:
                    reply += f"{5 - self.game_state.attempts} left to get ability name"
                else:
                    reply += "Type `_hint` to receive a hint"
                await message.channel.send(reply)

    @commands.command()
    async def guess_ability(self, ctx):
        if not self.is_game_active:
            self.game_state.start_game()
            self.game_state.ability = self.game_state.champion.get_random_ability()

            self.game_state.ability.get_image()
            thread = await ctx.channel.create_thread(
                name='loldle',
                type=discord.ChannelType.public_thread
            )
            await thread.send(file=discord.File("edited_ability.png"))
            self.game_state.thread = thread
            self.is_game_active = True

        else:
            await ctx.send("Game is being played now!")

    @commands.command()
    async def guess(self, ctx, champion: str):
        print('guess', ctx.message)
        if self.is_game_active and ctx.channel == self.game_state.thread:
            if self.game_state.guess(champion):
                await ctx.channel.send(f"{ctx.author} Guessed correct!\nIt took {self.game_state.attempts} attempts.")
                self.game_state.stop_game()
                self.is_game_active = False
            else:
                message = "Wrong champion.\n"
                if self.game_state.attempts < 5:
                    message += f"{5 - self.game_state.attempts} left to get ability name"
                else:
                    message += "Type `_hint` to receive a hint"
                await ctx.channel.send(message)

    @commands.command()
    async def hint(self, ctx):
        if ctx.channel == self.game_state.thread:
            if self.game_state.attempts < 5:
                await ctx.send(f"{5 - self.game_state.attempts} Attempts left to get the next hint")
            elif 5 <= self.game_state.attempts < 10:
                await ctx.send(f"Ability name: {self.game_state.ability.name}\n"
                               f"Next hint after {10 - self.game_state.attempts} attempts")
            else:
                await ctx.send(f"Ability name: {self.game_state.ability.name}", file=discord.File('ability.png'))


async def setup(bot):
    await bot.add_cog(GuessAbility(bot))
