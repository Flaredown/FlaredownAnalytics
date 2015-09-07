from flask import Flask
from flask_restful import Api, Resource
from .common.db import connect
from .common.util import to_json

app = Flask(__name__)
app.config.from_pyfile("../config.py")

db = connect(app.config)

api = Api(app)


class EntryAPI(Resource):
    def get(self):
        entry = db.entries.find_one()
        return {
            "_id": to_json(entry["_id"]),
            "user_id": entry["user_id"],
            "date": to_json(entry["date"]),
            "settings": entry["settings"],
            "conditions": entry["conditions"],
            "symptoms": entry["symptoms"],
            "responses": [{
                "name": response["name"],
                "value": response["value"],
                "catalog": response["catalog"],
            } for response in entry["responses"]],
            "conditions": entry["conditions"],
            "symptoms": entry["symptoms"],
            "treatments": [{
                "name": treatment["name"],
                "quantity": treatment["quantity"],
                "unit": treatment["unit"],
                "repetition": treatment["repetition"],
            } for treatment in entry["treatments"]],
        }


class UserAPI(Resource):
    def get(self, user_id):
        user = list(db.entries.find({"user_id": user_id}))
        return {"user_id": user_id, "entries": len(user)}


api.add_resource(EntryAPI, "/analytics/api/v1.0/entry")
api.add_resource(UserAPI, "/analytics/api/v1.0/user/<int:user_id>")
