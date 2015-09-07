from flask import Flask
from flask_restful import Api, Resource
from .common.db import connect
from .common.util import to_json

app = Flask(__name__)
app.config.from_pyfile("../config.py")

db = connect(app.config)

api = Api(app)


class TreatmentAPI(Resource):
    def get(self, name):
        entry = db.entries.find_one()
        return {"response": to_json(entry)}

api.add_resource(TreatmentAPI, "/analytics/api/v1.0/treatment/<name>")
