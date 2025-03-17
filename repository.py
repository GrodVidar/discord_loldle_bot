import json

from models import Champion
import csv


def populate_database(session, filename):
    with open(filename, "r") as f:
        champion_data = json.load(f)
        for data in champion_data:
            instance = session.query(Champion).filter(
                Champion.champion_id == data["id"]
            ).first()
            if instance:
                continue
            champion = Champion(
                data["id"],
                data["name"],
                data["gender"],
                data["position"],
                data["specie"],
                data["resource"],
                data["ranged_type"],
                data["region"],
                data["release_year"],
            )

            session.add(champion)
            print(champion.champion_id + " Added to db")
    session.commit()

def add_emojis(session, csv_file):
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            champion = session.query(Champion).filter(
                Champion.name == row["Champion"]).first()
            if champion:
                champion.emoji_1 = row["Emoji 1"]
                champion.emoji_2 = row["Emoji 2"]
                champion.emoji_3 = row["Emoji 3"]
                print(champion.name + " Added emojis")
            else:
                print(row["Champion"] + " not found in db")
        session.commit()
