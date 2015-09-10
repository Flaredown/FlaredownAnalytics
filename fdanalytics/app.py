from bson.objectid import ObjectId
from flask import Flask
from flask_restful import Api, Resource
from .common.db import connect
from .common.util import to_json

app = Flask(__name__)
app.config.from_pyfile("../config.py")

db = connect(app.config)

api = Api(app)


def _format_date(dt):
    return dt.strftime("%Y-%m-%d")


class EntryListAPI(Resource):
    def get(self):
        entry = db.entries.find_one()

        return {
            "_id": to_json(entry["_id"]),
            "user_id": entry["user_id"],
            "date": entry["date"],
            "settings": entry.get("settings"),
            "conditions": entry.get("conditions"),
            "symptoms": entry.get("symptoms"),
            "responses": [{
                "name": response["name"],
                "value": response["value"],
                "catalog": response["catalog"],
            } for response in entry["responses"]],
            "treatments": [{
                "name": treatment["name"],
                "quantity": treatment["quantity"],
                "unit": treatment["unit"],
                "repetition": treatment.get("repetition"),
            } for treatment in entry["treatments"]],
        }


class EntryAPI(Resource):
    def get(self, entry_id):
        entry = db.entries.find_one({"_id": entry_id})
        # TODO: replace with ObjectId(entry_id) when we're not stuck with couch _ids
        return {
            "_id": to_json(entry["_id"]),
            "user_id": entry["user_id"],
            "date": entry["date"],
            "settings": entry.get("settings"),
            "conditions": entry.get("conditions"),
            "symptoms": entry.get("symptoms"),
            "responses": [{
                "name": response["name"],
                "value": response["value"],
                "catalog": response["catalog"],
            } for response in entry["responses"]],
            "treatments": [{
                "name": treatment["name"],
                "quantity": treatment["quantity"],
                "unit": treatment["unit"],
                "repetition": treatment.get("repetition"),
            } for treatment in entry["treatments"]],
        }


class UserAPI(Resource):
    def get(self, user_id):
        user_entries = list(db.entries.find({"user_id": user_id})
                                      .sort("date", 1))

        return {
            "user_id": user_id,
            "settings": user_entries[-1].get("settings") if len(user_entries) > 0 else None,
            "num_entries": len(user_entries),
            "first_entry_date": user_entries[0]["date"] if len(user_entries) > 0 else None,
            "last_entry_date": user_entries[-1]["date"] if len(user_entries) > 0 else None,
        }


api.add_resource(EntryListAPI, "/analytics/api/v1.0/entries/")
api.add_resource(EntryAPI, "/analytics/api/v1.0/entries/<entry_id>/")

api.add_resource(UserAPI, "/analytics/api/v1.0/users/<user_id>/")
