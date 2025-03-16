import random
import urllib.request

import requests
from PIL import Image
from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String, Table,
                        func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, joinedload, reconstructor, relationship
from thefuzz import fuzz

Base = declarative_base()


class Skin(Base):
    __tablename__ = "skin"
    pk = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(Integer)
    image_url = Column(String)
    champion_pk = Column(Integer, ForeignKey("champion.pk"))

    def __init__(self, name, number, champion_id, **kwargs):
        super().__init__(**kwargs)
        self._x = 0
        self._y = 0
        self._width = 120
        self._height = 70
        self.name = name
        self.number = number
        self.image_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion_id}_{self.number}.jpg"

    @property
    def width_increase(self):
        return 60

    @property
    def height_increase(self):
        return 35

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @reconstructor
    def init_on_load(self):
        self._width = 120
        self._height = 70
        self._x = 0
        self._y = 0

    def zoom_at(self, img):
        w, h = img.size

        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        if self.x + self.width > w:
            self.width = w - self.x
        if self.y + self.height > h:
            self.height = h - self.y

        box = (self.x, self.y, self.x + self.width, self.y + self.height)
        img = img.crop(box)
        return img.resize((w, h), Image.Resampling.LANCZOS)

    def get_image(self):
        urllib.request.urlretrieve(self.image_url, "images/splash.jpg")
        with Image.open("images/splash.jpg") as im:
            w, h = im.size
            self.x = random.randint(150, w)
            self.y = random.randint(100, h)
            im = self.zoom_at(im)
            im.save("images/edited_splash.jpg")

    def zoom_out(self):
        self.x -= self.width_increase // 2
        self.y -= self.height_increase // 2
        self.width += self.width_increase
        self.height += self.height_increase
        with Image.open("images/splash.jpg") as im:
            im = self.zoom_at(im)
            im.save("images/edited_splash.jpg")


class Ability(Base):
    __tablename__ = "ability"
    pk = Column(Integer, primary_key=True)
    name = Column(String)
    is_passive = Column(Boolean)
    image_url = Column(String)
    patch = Column(String)
    champion_pk = Column(Integer, ForeignKey("champion.pk"))

    def __init__(self, name, is_passive, patch, image_endpoint, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.is_passive = is_passive
        self.patch = patch
        self.image_url = (
            f"https://ddragon.leagueoflegends.com/cdn/{self.patch}/img/"
            + ("passive/" if self.is_passive else "spell/")
            + image_endpoint
        )

    def get_image(self):
        urllib.request.urlretrieve(self.image_url, "images/ability.png")
        with Image.open("images/ability.png") as im:
            im = im.convert("LA")
            im = im.rotate(random.choice([0, 90, 180, 270]))
            im.save("images/edited_ability.png")

    def __str__(self):
        return f"ability_name: {self.name}, is_passive: {self.is_passive}"

    def __repr__(self):
        return f"ability_name: {self.name}, is_passive: {self.is_passive}"


champion_position = Table(
    "champion_position",
    Base.metadata,
    Column("champion_pk", Integer, ForeignKey("champion.pk")),
    Column("position_pk", Integer, ForeignKey("position.pk")),
)


class Position(Base):
    __tablename__ = "position"
    pk = Column(Integer, primary_key=True)
    name = Column(String)
    champions = relationship(
        "Champion", secondary=champion_position, back_populates="positions"
    )

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


champion_specie = Table(
    "champion_specie",
    Base.metadata,
    Column("champion_pk", Integer, ForeignKey("champion.pk")),
    Column("specie_pk", Integer, ForeignKey("specie.pk")),
)


class Specie(Base):
    __tablename__ = "specie"
    pk = Column(Integer, primary_key=True)
    name = Column(String)
    champions = relationship(
        "Champion", secondary=champion_specie, back_populates="species"
    )

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


champion_range_type = Table(
    "champion_range_type",
    Base.metadata,
    Column("champion_pk", Integer, ForeignKey("champion.pk")),
    Column("range_type_pk", Integer, ForeignKey("range_type.pk")),
)


class RangeType(Base):
    __tablename__ = "range_type"
    pk = Column(Integer, primary_key=True)
    type = Column(String)
    champions = relationship(
        "Champion", secondary=champion_range_type, back_populates="range_types"
    )

    def __repr__(self):
        return self.type

    def __str__(self):
        return self.type


champion_region = Table(
    "champion_region",
    Base.metadata,
    Column("champion_pk", Integer, ForeignKey("champion.pk")),
    Column("region_pk", Integer, ForeignKey("region.pk")),
)


class Region(Base):
    __tablename__ = "region"
    pk = Column(Integer, primary_key=True)
    name = Column(String)
    champions = relationship(
        "Champion", secondary=champion_region, back_populates="regions"
    )


class Champion(Base):
    __tablename__ = "champion"
    pk = Column(Integer, primary_key=True)
    champion_id = Column(String)
    name = Column(String)
    gender = Column(String)
    positions = relationship(
        "Position", secondary=champion_position, back_populates="champions"
    )
    species = relationship(
        "Specie", secondary=champion_specie, back_populates="champions"
    )
    resource = Column(String)
    range_types = relationship(
        "RangeType", secondary=champion_range_type, back_populates="champions"
    )
    regions = relationship(
        "Region", secondary=champion_region, back_populates="champions"
    )
    release_year = Column(Integer)
    skins = relationship("Skin", backref=backref("champion"))
    abilities = relationship("Ability", backref=backref("champion"))
    patch = Column(String)

    def __init__(
        self,
        champion_id,
        name,
        gender,
        positions,
        species,
        resource,
        range_types,
        regions,
        release_year,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.champion_id = champion_id
        self.name = name
        self.gender = gender
        self.positions = [Position(name=name) for name in positions]
        self.species = [Specie(name=name) for name in species]
        self.resource = resource
        self.range_types = [RangeType(type=type) for type in range_types]
        self.regions = [Region(name=name) for name in regions]
        self.release_year = release_year
        self.patch = self.get_latest_patch()
        data = self.get_champion_data()
        for ability in data["data"][self.champion_id]["spells"]:
            self.abilities.append(
                Ability(ability["name"], False, self.patch, ability["image"]["full"])
            )
        passive = data["data"][self.champion_id]["passive"]
        self.abilities.append(
            Ability(passive["name"], True, self.patch, passive["image"]["full"])
        )
        for skin in data["data"][self.champion_id]["skins"]:
            self.skins.append(Skin(skin["name"], skin["num"], self.champion_id))

    def __str__(self):
        return f"Champion name: {self.name}"

    def __repr__(self):
        return f"Champion name: {self.name}"

    def get_random_ability(self):
        return random.choice(self.abilities)

    def get_random_skin(self):
        return random.choice(self.skins)

    def get_champion_data(self):
        champion_url = f"https://ddragon.leagueoflegends.com/cdn/{self.patch}/data/en_US/champion/{self.champion_id}.json"
        response = requests.get(champion_url)
        print(response.status_code, champion_url)
        return response.json()

    @staticmethod
    def get_latest_patch():
        patch_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        response = requests.get(patch_url)
        data = response.json()
        return data[0]

    @staticmethod
    def get_random_champion(session):
        champion = (
            session.query(Champion)
            .options(
                joinedload(Champion.positions),
                joinedload(Champion.species),
                joinedload(Champion.range_types),
                joinedload(Champion.regions),
            )
            .order_by(func.random())
            .first()
        )
        print(champion)
        return champion


class GameState:
    threshold = 80

    def __init__(self, bot):
        self.bot = bot
        self.attempts = 0
        self.ability = None
        self.champion = None
        self.thread = None
        self.skin = None
        self.is_game_active = False

    async def stop_game(self):
        self.attempts = 0
        self.champion = None
        self.ability = None
        await self.thread.edit(archived=True)
        self.thread = None
        self.is_game_active = False

    def start_game(self):
        self.attempts = 0
        with self.bot.session as session:
            self.champion = Champion.get_random_champion(session)
        self.is_game_active = True

    def guess(self, guess: str):
        self.attempts += 1
        ratio = fuzz.ratio(self.champion.name.lower(), guess.lower())
        return ratio >= self.threshold
