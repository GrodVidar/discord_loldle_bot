import json

from models import Champion


def populate_database(session):
    with open("champion_data.json", "r") as f:
        champion_data = json.load(f)
        for data in champion_data:
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

    session.commit()
