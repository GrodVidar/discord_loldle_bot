import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from models import Champion, GameState


class GuessClassic(commands.Cog):
    GREEN = (9, 193, 46)
    YELLOW = (217, 126, 11)
    RED = (218, 21, 15)

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
                    f"The correct answer was: {self.game_state.champion.name}"
                )
                await self.game_state.stop_game()
                return
            comparison = self.compare_champions(message.content)
            await message.channel.send(**comparison)
            if self.game_state.guess(message.content):
                await message.channel.send(
                    f"{message.author.nick if message.author.nick else message.author.display_name} guessed correct!\n"
                    f"It took {self.game_state.attempts} attempts."
                )
                await self.game_state.stop_game()

    @commands.command()
    async def guess_classic(self, ctx):
        if not self.game_state.is_game_active:
            self.game_state.start_game()
            thread = await ctx.channel.create_thread(
                name="Guess Classic", type=discord.ChannelType.public_thread
            )
            await thread.send("*Type `give_up` to give up*")
            self.game_state.thread = thread
        else:
            await ctx.send("Game is being played now!")

    def compare_champions(self, champion_name):
        champion = (
            self.bot.session.query(Champion)
            .options(
                joinedload(Champion.positions),
                joinedload(Champion.species),
                joinedload(Champion.range_types),
                joinedload(Champion.regions),
            )
            .filter(
                or_(
                    func.lower(Champion.name) == func.lower(champion_name),
                    func.lower(Champion.champion_id) == func.lower(champion_name),
                )
            )
            .first()
        )
        print(champion)
        if champion:
            self.compare_attribute(
                champion.gender, self.game_state.champion.gender, "gender"
            )
            self.compare_attributes(
                [x.name for x in champion.positions],
                [x.name for x in self.game_state.champion.positions],
                "position",
            )
            self.compare_attributes(
                [x.name for x in champion.species],
                [x.name for x in self.game_state.champion.species],
                "species",
            )
            self.compare_attribute(
                champion.resource, self.game_state.champion.resource, "resources"
            )
            self.compare_attributes(
                [x.type for x in champion.range_types],
                [x.type for x in self.game_state.champion.range_types],
                "range_types",
            )
            self.compare_attributes(
                [x.name for x in champion.regions],
                [x.name for x in self.game_state.champion.regions],
                "regions",
            )
            self.compare_years(
                champion.release_year,
                self.game_state.champion.release_year,
                "release_year",
            )
            return {
                "content": champion.name,
                "files": [
                    discord.File("images/classic/gender.png"),
                    discord.File("images/classic/position.png"),
                    discord.File("images/classic/species.png"),
                    discord.File("images/classic/resources.png"),
                    discord.File("images/classic/range_types.png"),
                    discord.File("images/classic/regions.png"),
                    discord.File("images/classic/release_year.png"),
                ],
            }
        else:
            self.game_state.attempts -= 1
            return {"content": "No champion with such name, no attempt counted"}

    def compare_attribute(
        self, champion_attribute, correct_champion_attribute, filename
    ):
        if champion_attribute == correct_champion_attribute:
            self.create_box(self.GREEN, champion_attribute, filename)
        else:
            self.create_box(self.RED, champion_attribute, filename)

    def compare_attributes(
        self, champion_attributes, correct_champion_attributes, filename
    ):
        if champion_attributes == correct_champion_attributes:
            self.create_box(self.GREEN, ",\n".join(champion_attributes), filename)
        elif any(x in champion_attributes for x in correct_champion_attributes):
            self.create_box(self.YELLOW, ",\n".join(champion_attributes), filename)
        else:
            self.create_box(self.RED, ",\n".join(champion_attributes), filename)

    def compare_years(self, champion_year, correct_champion_year, filename):
        if champion_year < correct_champion_year:
            self.create_box(self.RED, str(champion_year), filename, "lt")
        elif champion_year > correct_champion_year:
            self.create_box(self.RED, str(champion_year), filename, "gt")
        else:
            self.create_box(self.GREEN, str(champion_year), filename)

    @staticmethod
    def create_box(color, attributes, filename, arrow=None):
        width, height = (198, 219)
        if arrow == "gt":
            img = Image.open("images/classic/templates/arrow_down.png")
        elif arrow == "lt":
            img = Image.open("images/classic/templates/arrow_up.png")
        else:
            img = Image.new("RGB", (width, height), color=color)

        draw = ImageDraw.Draw(img)
        draw.text(
            (100, 100),
            f"{filename}\n{attributes}",
            fill=(0, 0, 0),
            align="center",
            anchor="mm",
            font_size=25,
        )
        img.save("images/classic/" + filename + ".png")


async def setup(bot):
    await bot.add_cog(GuessClassic(bot))
