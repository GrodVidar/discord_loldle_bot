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
        if self.is_game_active and not message.author.bot:
            if self.game_state.guess(message.content):
                await message.channel.send(
                    f"{message.author} Guessed correct!\nIt took {self.game_state.attempts} attempts."
                )
                self.game_state.stop_game()
                self.is_game_active = False
            else:
                await message.channel.send("Wrong champion")

    @commands.command()
    async def guess_ability(self, ctx):
        if not self.is_game_active:
            self.game_state.start_game()
            self.game_state.ability = self.game_state.champion.get_random_ability()

            self.game_state.ability.get_image()

            await ctx.send(file=discord.File("edited_ability.png"))
            self.is_game_active = True

        else:
            await ctx.send("Game is being played now!")

    @commands.command()
    async def guess(self, ctx, champion: str):
        print('guess', ctx.message)
        if self.is_game_active:
            if self.game_state.guess(champion):
                await ctx.channel.send(f"{ctx.author} Guessed correct!\nIt took {self.game_state.attempts} attempts.")
                self.game_state.stop_game()
                self.is_game_active = False
            else:
                await ctx.channel.send("Wrong champion ")


async def setup(bot):
    await bot.add_cog(GuessAbility(bot))
