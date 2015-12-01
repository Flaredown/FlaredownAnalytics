from flask import g, abort
from flask_restful import Resource, inputs, reqparse
from ..common.util import ignore_case


n_conditions = [
    {
        "$group": {
            "_id": "$user_id",
            "conditions": {"$addToSet": "$conditions"}
        }
    },
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
    },
    {
        "$sort": {"_id": 1}
    }
]

n_symptoms = [
    {
        "$group": {
            "_id": "$user_id",
            "symptoms": {"$addToSet": "$symptoms"}
        }
    },
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
    },
    {
        "$sort": {"_id": 1}
    }
]

n_treatments = [
    {
        "$group": {
            "_id": "$user_id",
            "treatments": {"$addToSet": "$treatments"}
        }
    },
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
    },
    {
        "$sort": {"_id": 1}
    }
]

top_conditions = [
    {
        "$unwind": "$conditions"
    },
    {
        "$group": {
            "_id": {
                "user_id": "$user_id",
            },
            "count": {"$sum": 1},
            "conditions": {"$addToSet": "$conditions"}
        }
    },
    {
        "$unwind": "$conditions"
    },
    {
        "$group": {
            "_id": {
                "condition": "$conditions"
            },
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$limit": 10
    },
    {
        "$project": {"_id": "$_id.condition", "count": "$count"}
    }
]

top_symptoms = [
    {
        "$unwind": "$symptoms"
    },
    {
        "$group": {
            "_id": {
                "user_id": "$user_id",
            },
            "count": {"$sum": 1},
            "symptoms": {"$addToSet": "$symptoms"}
        }
    },
    {
        "$unwind": "$symptoms"
    },
    {
        "$group": {
            "_id": {
                "symptom": "$symptoms"
            },
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$limit": 10
    },
    {
        "$project": {"_id": "$_id.symptom", "count": "$count"}
    }
]

top_treatments = [
    {
        "$unwind": "$treatments"
    },
    {
        "$group": {
            "_id": {
                "user_id": "$user_id",
            },
            "count": {"$sum": 1},
            "treatments": {"$addToSet": "$treatments.name"}
        }
    },
    {
        "$unwind": "$treatments"
    },
    {
        "$group": {
            "_id": {
                "treatment": "$treatments"
            },
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$limit": 10
    },
    {
        "$project": {"_id": "$_id.treatment", "count": "$count"}
    }
]

n_users = [
    {
        "$group": {"_id": "$user_id"}
    }
]


class SegmentAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("condition")
        parser.add_argument("symptom")
        parser.add_argument("treatment")
        parser.add_argument("compare", type=inputs.boolean)
        args = parser.parse_args()

        match = []

        if args.get("condition"):
            match.append({"$match": {"conditions": ignore_case(args.get("condition"))}})
        if args.get("symptom"):
            match.append({"$match": {"symptoms": ignore_case(args.get("symptom"))}})
        if args.get("treatment"):
            match.append({"$match": {"treatments.name": ignore_case(args.get("treatment"))}})

        if args.get("compare"):

            and_not_queries = []

            if args.get("condition"):
                and_not_queries.append({"conditions": {"$not": ignore_case(args.get("condition"))}})
            if args.get("symptom"):
                and_not_queries.append({"symptoms": {"$not": ignore_case(args.get("symptom"))}})
            if args.get("treatment"):
                and_not_queries.append({"treatments.name": {"$not": ignore_case(args.get("treatment"))}})

            if len(and_not_queries) == 0:
                abort(400, "Cannot compare segments without a condition, symptom, or treatment by which to segment.")

            complement = [{"$match": {"$or": and_not_queries}}]

            group_by = [{k: v, "comparison": "eq"}
                        for (k, v) in args.items()
                        if v and k != "compare"]
            # should make it clear that the complement is ALL not matched by the main query
            # demorgan's law: or(not(X), not(Y)) == not(and(X, Y))
            group_by_complement = [{k: v, "comparison": "ne"}
                                   for (k, v) in args.items()
                                   if v and k != "compare"]

            return {
                "segments": {
                    "n_users": [
                        {
                            "groupBy": group_by,
                            "values": len(list(g.db.entries.aggregate(pipeline=match + n_users)))
                        },
                        {
                            "groupBy": group_by_complement,
                            "values": len(list(g.db.entries.aggregate(pipeline=complement + n_users)))
                        }
                    ],
                    "n_conditions": [
                        {
                            "groupBy": group_by,
                            "values": list(g.db.entries.aggregate(pipeline=match + n_conditions))
                        },
                        {
                            "groupBy": group_by_complement,
                            "values": list(g.db.entries.aggregate(pipeline=complement + n_conditions))
                        }
                    ],
                    "top_conditions": [
                        {
                            "groupBy": group_by,
                            "values": list(g.db.entries.aggregate(pipeline=match + top_conditions))
                        },
                        {
                            "groupBy": group_by_complement,
                            "values": list(g.db.entries.aggregate(pipeline=complement + top_conditions))
                        }
                    ],
                    "n_symptoms": [
                        {
                            "groupBy": group_by,
                            "values": list(g.db.entries.aggregate(pipeline=match + n_symptoms))
                        },
                        {
                            "groupBy": group_by_complement,
                            "values": list(g.db.entries.aggregate(pipeline=complement + n_symptoms))
                        }
                    ],
                    "top_symptoms": [
                        {
                            "groupBy": group_by,
                            "values": list(g.db.entries.aggregate(pipeline=match + top_symptoms))
                        },
                        {
                            "groupBy": group_by_complement,
                            "values": list(g.db.entries.aggregate(pipeline=complement + top_symptoms))
                        }
                    ],
                    "n_treatments": [
                        {
                            "groupBy": group_by,
                            "values": list(g.db.entries.aggregate(pipeline=match + n_treatments))
                        },
                        {
                            "groupBy": group_by_complement,
                            "values": list(g.db.entries.aggregate(pipeline=complement + n_treatments))
                        }
                    ],
                    "top_treatments": [
                        {
                            "groupBy": group_by,
                            "values": list(g.db.entries.aggregate(pipeline=match + top_treatments))
                        },
                        {
                            "groupBy": group_by_complement,
                            "values": len(list(g.db.entries.aggregate(pipeline=complement + top_treatments)))
                        }
                    ],
                }
            }

        return {
            "segments": {
                "n_users": len(list(g.db.entries.aggregate(pipeline=match + n_users))),
                "n_conditions": list(g.db.entries.aggregate(pipeline=match + n_conditions)),
                "top_conditions": list(g.db.entries.aggregate(pipeline=match + top_conditions)),
                "n_symptoms": list(g.db.entries.aggregate(pipeline=match + n_symptoms)),
                "top_symptoms": list(g.db.entries.aggregate(pipeline=match + top_symptoms)),
                "n_treatments": list(g.db.entries.aggregate(pipeline=match + n_treatments)),
                "top_treatments": list(g.db.entries.aggregate(pipeline=match + top_treatments)),
            }
        }
