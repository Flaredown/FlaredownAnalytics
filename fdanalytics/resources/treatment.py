from flask import g
from flask_restful import Resource
from ..common.util import ignore_case


class TreatmentListAPI(Resource):
    def get(self):
        return {
            "all": g.db.entries.distinct("treatments.name")
        }


class TreatmentAPI(Resource):
    def get(self, treatment_name):
        # TODO: len(distinct) won't scale well, use aggregation pipeline instead

        unit_stats = [
            {"$unwind": "$treatments"},
            {"$match": {"treatments.name": ignore_case(treatment_name)}},
            {"$group": {"_id": "$treatments.unit",
                        "num_entries": {"$sum": 1},
                        "avg_dose": {"$avg": {"$multiply": ["$treatments.quantity", "$treatments.repetition"]}}}}
        ]

        return {
            "name": treatment_name.lower(),
            "num_entries": g.db.entries.count({"treatments.name": ignore_case(treatment_name)}),
            "num_users": len(g.db.entries.distinct("user_id", {"treatments.name": ignore_case(treatment_name)})),
            "units": list(g.db.entries.aggregate(pipeline=unit_stats)),
        }
