import re
from bson.objectid import ObjectId
from flask import Flask
from flask_restful import Api, Resource
from .common.db import connect

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


class ConditionListAPI(Resource):
    def get(self):
        n_conditions = [
            {
                "$project": {
                    "nConditions": {"$size": {"$ifNull": ["$conditions", []]}}
                }
            },
            {
                "$project": {
                    "conditionsLowerBound": {
                        "$subtract": ["$nConditions", {"$mod": ["$nConditions", 1]}]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$conditionsLowerBound",
                    "count": {"$sum": 1}
                }
            }
        ]
        return {
            "all": db.entries.distinct("conditions"),
            "distribution": list(db.entries.aggregate(n_conditions))
        }


class EntryListAPI(Resource):
    def get(self):
        return [{
            "_id": str(entry["_id"]),
            "user_id": entry.get("user_id"),
            "date": str(entry.get("date")),
        } for entry in db.entries.find().sort("date", 1)]


class EntryAPI(Resource):
    def get(self, entry_id):
        entry = db.entries.find_one({"_id": entry_id})
        # TODO: replace with ObjectId(entry_id) when we're not stuck with couch _ids
        return {
            "_id": str(entry["_id"]),
            "user_id": entry["user_id"],
            "date": str(entry["date"]),
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


class SymptomListAPI(Resource):
    def get(self):
        n_symptoms = [
            {
                "$project": {
                    "nSymptoms": {"$size": {"$ifNull": ["$symptoms", []]}}
                }
            },
            {
                "$project": {
                    "symptomsLowerBound": {
                        "$subtract": ["$nSymptoms", {"$mod": ["$nSymptoms", 1]}]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$symptomsLowerBound",
                    "count": {"$sum": 1}
                }
            }
        ]
        return {
            "all": db.entries.distinct("symptoms"),
            "distribution": list(db.entries.aggregate(n_symptoms))
        }


class TreatmentListAPI(Resource):
    def get(self):

        n_treatments = [
            {
                "$project": {
                    "nTreatments": {"$size": {"$ifNull": ["$treatments", []]}}
                }
            },
            {
                "$project": {
                    "treatmentsLowerBound": {
                        "$subtract": ["$nTreatments", {"$mod": ["$nTreatments", 1]}]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$treatmentsLowerBound",
                    "count": {"$sum": 1}
                }
            }
        ]

        return {
            "all": db.entries.distinct("treatments.name"),
            "distribution": list(db.entries.aggregate(pipeline=n_treatments))
        }


class TreatmentAPI(Resource):
    def get(self, treatment_name):
        # TODO: len(distinct) won't scale well, use aggregation pipeline instead

        treatment_name_ignorecase = re.compile(treatment_name, re.IGNORECASE)

        unit_stats = [
            {"$unwind": "$treatments"},
            {"$match": {"treatments.name": treatment_name_ignorecase}},
            {"$group": {"_id": "$treatments.unit",
                        "num_entries": {"$sum": 1},
                        "avg_dose": {"$avg": {"$multiply": ["$treatments.quantity", "$treatments.repetition"]}}}}
        ]

        return {
            "name": treatment_name.lower(),
            "num_entries": db.entries.count({"treatments.name": treatment_name_ignorecase}),
            "num_users": len(db.entries.distinct("user_id", {"treatments.name": treatment_name_ignorecase})),
            "units": list(db.entries.aggregate(pipeline=unit_stats)),
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

api.add_resource(ConditionListAPI, "/analytics/api/v1.0/conditions/")

api.add_resource(EntryListAPI, "/analytics/api/v1.0/entries/")
api.add_resource(EntryAPI, "/analytics/api/v1.0/entries/<entry_id>/")

api.add_resource(SymptomListAPI, "/analytics/api/v1.0/symptoms/")

api.add_resource(TreatmentListAPI, "/analytics/api/v1.0/treatments/")
api.add_resource(TreatmentAPI, "/analytics/api/v1.0/treatments/<treatment_name>")

api.add_resource(UserListAPI, "/analytics/api/v1.0/users/")
api.add_resource(UserAPI, "/analytics/api/v1.0/users/<user_id>/")
