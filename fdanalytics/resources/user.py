from flask import g
from flask_restful import Resource
from ..common.util import safe_index


class UserAPI(Resource):
    def get(self, user_id):
        user_entries = list(g.db.entries.find({"user_id": user_id})
                                        .sort("date", 1))

        return {
            "user_id": user_id,
            "settings": safe_index(user_entries, -1, default_value={}).get("settings"),
            "num_entries": len(user_entries),
            "entries": user_entries,
            "first_entry_date": safe_index(user_entries, 0, default_value={}).get("date"),
            "last_entry_date": safe_index(user_entries, -1, default_value={}).get("date"),
        }
