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
            "date": _format_date(entry["date"]),
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
            "first_entry_date": _format_date(user_entries[0]["date"]) if len(user_entries) > 0 else None,
            "last_entry_date": _format_date(user_entries[-1]["date"]) if len(user_entries) > 0 else None,
        }


api.add_resource(EntryListAPI, "/analytics/api/v1.0/entries")
api.add_resource(UserAPI, "/analytics/api/v1.0/users/<int:user_id>")
