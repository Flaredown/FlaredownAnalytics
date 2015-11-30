from flask import g
from flask_restful import Resource


class SymptomListAPI(Resource):
    def get(self):
        return {
            "all": g.db.entries.distinct("symptoms")
        }
