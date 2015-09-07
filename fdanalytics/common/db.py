from pymongo import MongoClient


def connect(config):
    client = MongoClient("mongodb://{}:{}".format(
        config["MONGO_HOST"],
        config["MONGO_PORT"]))
    db = client[config["DB_NAME"]]

    return db
