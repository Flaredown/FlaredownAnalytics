import json
from pymongo import MongoClient

USER_ID = "colingorrie"
PASSWORD = "testing123"
HOST = "ds041581.mongolab.com"
PORT = 41581
DB = "flaredown-staging"

if __name__ == "__main__":
    # client = MongoClient("mongodb://localhost:27017/")
    client = MongoClient("mongodb://{user_id}:{password}@{host}:{port}/{db}".format(
        user_id=USER_ID,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        db=DB,
    ))
    db = client.get_default_database()
    entries = db.entries

    # entries.remove()

    with open("dump.json") as f:
        couch_entries = [row["doc"] for row in json.load(f)["rows"]]

        entries.insert_many(couch_entries)

    # results = entries.distinct("treatments.name")

    # print(list(results))

    # results = entries.aggregate([
    #     {
    #         "$unwind": "$conditions"
    #     },
    #     {
    #         "$group": {
    #             "_id": {
    #                 "user_id": "$user_id",
    #                 "sex": "$settings.sex"
    #             },
    #             "count": {"$sum": 1},
    #             "conditions": {"$addToSet": "$conditions"}
    #         }
    #     },
    #     {
    #         "$unwind": "$conditions"
    #     },
    #     {
    #         "$group": {
    #             "_id": {
    #                 "sex": "$_id.sex",
    #                 "condition": "$conditions"
    #             },
    #             "count": {"$sum": 1}
    #         }
    #     }
    # ])

    # print(list(results))

    client.close()
