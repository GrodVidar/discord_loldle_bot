import json

from models import Champion


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
