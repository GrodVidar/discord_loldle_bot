import requests
import random
import urllib.request
from PIL import Image


def get_champions(is_random=False):
    champions_url = 'https://ddragon.leagueoflegends.com/cdn/14.7.1/data/en_US/champion.json'
    response = requests.get(champions_url)
    if response.status_code == 200:
        champions_data = response.json()
        if is_random:
            champion = random.choice(list(champions_data['data']))
            return champions_data['data'][champion]['name'], champions_data['data'][champion]['id']
        else:
            champions = []
            for champion in champions_data['data']:
                champions.append((champions_data['data'][champion]['name'], champions_data['data'][champion]['id']))
            return champions


def get_champion_data(champion_name):
    champion_url = f'https://ddragon.leagueoflegends.com/cdn/14.7.1/data/en_US/champion/{champion_name}.json'
    response = requests.get(champion_url)
    return response.json()


class Skin:
    def __init__(self, data, champion_id):
        self.name = data['name']
        self.number = data['num']
        self.image_url = f'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion_id}_{self.number}.jpg'
        self.width_increase = 60
        self.height_increase = 35
        self.width = 120
        self.height = 70
        self.x = 0
        self.y = 0

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
        urllib.request.urlretrieve(self.image_url, 'images/splash.jpg')
        with Image.open('images/splash.jpg') as im:
            w, h = im.size
            self.x = random.randint(150, w)
            self.y = random.randint(100, h)
            im = self.zoom_at(im)
            im.save('images/edited_splash.jpg')

    def zoom_out(self):
        self.x -= self.width_increase // 2
        self.y -= self.height_increase // 2
        self.width += self.width_increase
        self.height += self.height_increase
        with Image.open('images/splash.jpg') as im:
            im = self.zoom_at(im)
            im.save('images/edited_splash.jpg')


class Ability:
    def __init__(self, data, is_passive):
        self.name = data['name']
        self.is_passive = is_passive
        self.image_url = ('https://ddragon.leagueoflegends.com/cdn/14.7.1/img/' +
                          ('passive/' if self.is_passive else 'spell/') + data['image']['full'])

    def get_image(self):
        urllib.request.urlretrieve(self.image_url, 'images/ability.png')
        with Image.open('images/ability.png') as im:
            im = im.convert('LA')
            im = im.rotate(random.choice([0, 90, 180, 270]))
            im.save('images/edited_ability.png')

    def __str__(self):
        return f"ability_name: {self.name}, is_passive: {self.is_passive}"

    def __repr__(self):
        return f"ability_name: {self.name}, is_passive: {self.is_passive}"


class Champion:
    def __init__(self):
        self.name, self.id = get_champions(True)
        data = get_champion_data(self.id)
        self.is_mana_user = data['data'][self.id]['partype'] == 'Mana'
        self.abilities = []
        for ability in data['data'][self.id]['spells']:
            self.abilities.append(Ability(ability, False))
        self.abilities.append(
            Ability(data['data'][self.id]['passive'], True)
        )
        self.skins = []
        for skin in data['data'][self.id]['skins']:
            self.skins.append(Skin(skin, self.id))

    def get_random_ability(self):
        return random.choice(self.abilities)

    def get_random_skin(self):
        return random.choice(self.skins)


class GameState:
    def __init__(self):
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
        self.champion = Champion()
        self.is_game_active = True

    def guess(self, champion: str):
        self.attempts += 1
        if (champion.lower().replace(' ', '').replace("'", '') ==
                self.champion.name.lower().replace(' ', '').replace("'", '')):
            return True
        return False
