from bson.objectid import ObjectId
from flask import Flask
from flask_restful import Api, Resource
from .common.db import connect
from .common.util import to_json

app = Flask(__name__)
app.config.from_pyfile("../config.py")

db = connect(app.config)

api = Api(app)


def _safe_index(list, i, default_value=None):
    try:
        el = list[i]
    except IndexError:
        el = default_value

    return el


class EntryListAPI(Resource):
    def get(self):
        return [{
            "_id": str(entry["_id"]),
            "user_id": entry.get("user_id"),
            "date": entry["date"],
        } for entry in db.entries.find().sort("date", 1)]


class EntryAPI(Resource):
    def get(self, entry_id):
        entry = db.entries.find_one({"_id": entry_id})
        # TODO: replace with ObjectId(entry_id) when we're not stuck with couch _ids
        return {
            "_id": str(entry["_id"]),
            "user_id": entry["user_id"],
            "date": entry["date"],
            "settings": entry.get("settings"),
            "conditions": entry.get("conditions"),
            "symptoms": entry.get("symptoms"),
            "responses": [{
                "name": response.get("name"),
                "value": response.get("value"),
                "catalog": response.get("catalog"),
            } for response in entry.get("responses")],
            "treatments": [{
                "name": treatment.get("name"),
                "quantity": treatment.get("quantity"),
                "unit": treatment.get("unit"),
                "repetition": treatment.get("repetition"),
            } for treatment in entry.get("treatments")],
        }


class UserListAPI(Resource):
    def get(self):
        return db.entries.distinct("user_id")


class UserAPI(Resource):
    def get(self, user_id):
        user_entries = list(db.entries.find({"user_id": user_id})
                                      .sort("date", 1))

        return {
            "user_id": user_id,
            "settings": _safe_index(user_entries, -1, default_value={}).get("settings"),
            "num_entries": len(user_entries),
            "first_entry_date": _safe_index(user_entries, 0, default_value={}).get("date"),
            "last_entry_date": _safe_index(user_entries, -1, default_value={}).get("date"),
        }


api.add_resource(EntryListAPI, "/analytics/api/v1.0/entries/")
api.add_resource(EntryAPI, "/analytics/api/v1.0/entries/<entry_id>/")

api.add_resource(UserListAPI, "/analytics/api/v1.0/users/")
api.add_resource(UserAPI, "/analytics/api/v1.0/users/<user_id>/")
