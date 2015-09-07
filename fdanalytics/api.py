from flask import Flask
from flask_restful import Api
from .resources.treatment import TreatmentAPI


app = Flask(__name__)
api = Api(app)

api.add_resource(TreatmentAPI, "/analytics/api/v1.0/treatment/<name>")
