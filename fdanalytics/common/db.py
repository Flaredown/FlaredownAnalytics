import os
from pymongo import MongoClient


def connect(config):
    if os.environ.get("HEROKU"):
        client = MongoClient("mongodb://{}:{}@{}:{}/{}".format(
            os.environ.get("USER_ID"),
            os.environ.get("PASSWORD"),
            os.environ.get("MONGO_HOST"),
            os.environ.get("MONGO_PORT"),
            os.environ.get("DB_NAME")))
    elif config["USER_ID"] and config["PASSWORD"]:
        client = MongoClient("mongodb://{}:{}@{}:{}/{}".format(
            config["USER_ID"],
            config["PASSWORD"],
            config["MONGO_HOST"],
            config["MONGO_PORT"],
            config["DB_NAME"]))
    else:
        client = MongoClient("mongodb://{}:{}/{}".format(
            config["MONGO_HOST"],
            config["MONGO_PORT"],
            config["DB_NAME"]))

    db = client.get_default_database()

    return db
