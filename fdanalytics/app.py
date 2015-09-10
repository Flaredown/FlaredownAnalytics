from flask import Flask
from flask_restful import Api, Resource
from .common.db import connect
from .common.util import to_json

app = Flask(__name__)
app.config.from_pyfile("../config.py")

db = connect(app.config)

api = Api(app)


class EntryListAPI(Resource):
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
        user_entries = list(db.entries.find({"user_id": user_id})
                                      .sort("date", 1))

        return {
            "user_id": user_id,
            "num_entries": len(user_entries),
            "first_entry_date": to_json(user_entries[0]["date"]) if len(user_entries) > 0 else None,
            "last_entry_date": to_json(user_entries[-1]["date"]) if len(user_entries) > 0 else None,
        }


api.add_resource(EntryListAPI, "/analytics/api/v1.0/entries")
api.add_resource(UserAPI, "/analytics/api/v1.0/users/<int:user_id>")
