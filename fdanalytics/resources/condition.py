from flask import g
from flask_restful import Resource


class ConditionListAPI(Resource):
    def get(self):
        return {
            "conditions": g.db.entries.distinct("conditions")
        }
