from pymongo import MongoClient


def connect(config):
    if config["USER_ID"] and config["PASSWORD"]:
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
