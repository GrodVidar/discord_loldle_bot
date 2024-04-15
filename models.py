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


class Ability:
    def __init__(self, data, is_passive):
        self.name = data['name']
        self.is_passive = is_passive
        self.image_url = ('https://ddragon.leagueoflegends.com/cdn/14.7.1/img/' +
                          ('passive/' if self.is_passive else 'spell/') + data['image']['full'])

    def get_image(self):
        urllib.request.urlretrieve(self.image_url, 'ability.png')
        with Image.open('ability.png') as im:
            im = im.convert('LA')
            im = im.rotate(random.choice([0, 90, 180, 270]))
            im.save('edited_ability.png')



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

    def get_random_ability(self):
        return random.choice(self.abilities)


class GameState:
    ability = None
    champion = None
    thread = None

    def __init__(self):
        self.attempts = 0

    def stop_game(self):
        self.attempts = 0
        self.champion = None
        self.ability = None
        self.thread = None

    def start_game(self):
        self.attempts = 0
        self.champion = Champion()

    def guess(self, champion: str):
        self.attempts += 1
        if (champion.lower().replace(' ', '').replace("'", '') ==
                self.champion.name.lower().replace(' ', '').replace("'", '')):
            return True
        return False
