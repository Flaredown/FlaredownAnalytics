import datetime
import json
from pymongo import MongoClient

USER_ID = "colingorrie"
PASSWORD = "testing123"
HOST = "ds051553.mongolab.com"
PORT = 51553
DB = "production-test"


def _dt_format(dt):
    return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%fZ")


def _to_list(s):
    if s is None:
        return []

    s = s.replace("\'", "")
    s = s.replace("\"", "")
    s = s.lstrip("[")
    s = s.rstrip("]")
    return s.split(",")


def normalize(entry):
    del entry["_id"]
    del entry["_rev"]

    for key in entry["settings"].keys():
        safe_key = key.replace(".", "U+FF0E")
        safe_key = safe_key.replace("$", "U+FF04")
        if key != safe_key:
            entry["settings"][safe_key] = entry["settings"].pop(key)

    entry["created_at"] = _dt_format(entry["created_at"])
    entry["settings"]["dobDay"] = int(entry["settings"]["dobDay"])
    entry["settings"]["dobMonth"] = int(entry["settings"]["dobMonth"])
    entry["settings"]["dobYear"] = int(entry["settings"]["dobYear"])
    entry["settings"]["ethnicOrigin"] = _to_list(entry["settings"].get("ethnicOrigin"))
    entry["settings"]["onboarded"] = True if entry["settings"]["onboarded"] == "true" else False
    entry["updated_at"] = _dt_format(entry["updated_at"])
    entry["user_id"] = int(entry["user_id"])
    return entry


if __name__ == "__main__":
    client = MongoClient("mongodb://{user_id}:{password}@{host}:{port}/{db}".format(
        user_id=USER_ID,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        db=DB,
    ))
    db = client.get_default_database()
    entries = db.entries

    entries.remove()

    with open("prod_dump.json") as f:
        couch_entries = [normalize(row["doc"]) for row in json.load(f)["rows"] if row["id"] != "_design/Entry"]

        # for e in couch_entries:
        #     print(e)

        entries.insert_many(couch_entries)

    client.close()
