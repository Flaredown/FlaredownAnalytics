from flask import Flask
from flask_restful import Api
from pymongo import MongoClient
from .resources.treatment import TreatmentAPI


app = Flask(__name__)
app.config.from_pyfile("../config.py")

client = MongoClient("mongodb://{}:{}".format(
    app.config["MONGO_HOST"],
    app.config["MONGO_PORT"]))

api = Api(app)

api.add_resource(TreatmentAPI, "/analytics/api/v1.0/treatment/<name>")
