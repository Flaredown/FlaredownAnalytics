import datetime
import json
from pymongo import MongoClient

USER_ID = "colingorrie"
PASSWORD = "testing123"
HOST = "ds041581.mongolab.com"
PORT = 41581
DB = "flaredown-staging"


def normalize_dt(date):
    try:
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    except:
        dt = date
    return dt


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

    # print(entries.find({"user_id": 9999}).count())

    for result in entries.find():
        clean_dt = normalize_dt(result.get("date"))
        # db.entries.update({"_id": result["_id"]}, {"$set": {"oldDate": result.get("date", None)}})
        db.entries.update({"_id": result["_id"]}, {"$set": {"date": clean_dt}})
