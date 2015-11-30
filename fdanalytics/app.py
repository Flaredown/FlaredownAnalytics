from bson.objectid import ObjectId
from flask import Flask, Blueprint, g
from flask_restful import Api, Resource
from flask.ext.heroku import Heroku
from werkzeug.contrib.fixers import ProxyFix
from .common.db import configure_client, connect
from .resources.condition import ConditionListAPI
from .resources.root import RootAPI
from .resources.segment import SegmentAPI
from .resources.treatment import TreatmentAPI, TreatmentListAPI
from .resources.user import UserAPI


app = Flask(__name__)
app.config.from_pyfile("../config.py")
app.wsgi_app = ProxyFix(app.wsgi_app)

client = configure_client(app.config)
db = connect(client)

api_bp = Blueprint("api", __name__)
api = Api(api_bp)


class EntryListAPI(Resource):
    def get(self):
        return [{
            "_id": str(entry["_id"]),
            "user_id": entry.get("user_id"),
            "date": str(entry.get("date")),
        } for entry in db.entries.find().sort("date", 1)]


class EntryAPI(Resource):
    def get(self, entry_id):
        entry = db.entries.find_one({"_id": ObjectId(entry_id)})
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
        return {
            "all": db.entries.distinct("symptoms")
        }


# class UserAPI(Resource):
#     def get(self, user_id):
#         user_entries = list(db.entries.find({"user_id": user_id})
#                                       .sort("date", 1))

#         return {
#             "user_id": user_id,
#             "settings": _safe_index(user_entries, -1, default_value={}).get("settings"),
#             "num_entries": len(user_entries),
#             "first_entry_date": _safe_index(user_entries, 0, default_value={}).get("date"),
#             "last_entry_date": _safe_index(user_entries, -1, default_value={}).get("date"),
#         }


api.add_resource(RootAPI, "/analytics/api/v1.0")

api.add_resource(ConditionListAPI, "/analytics/api/v1.0/conditions/")

api.add_resource(EntryListAPI, "/analytics/api/v1.0/entries/")
api.add_resource(EntryAPI, "/analytics/api/v1.0/entries/<entry_id>")

api.add_resource(SymptomListAPI, "/analytics/api/v1.0/symptoms/")

api.add_resource(TreatmentListAPI, "/analytics/api/v1.0/treatments/")
api.add_resource(TreatmentAPI, "/analytics/api/v1.0/treatments/<treatment_name>")

api.add_resource(UserAPI, "/analytics/api/v1.0/users/<user_id>")

api.add_resource(SegmentAPI, "/analytics/api/v1.0/segments")

app.register_blueprint(api_bp)


@app.before_request
def before_request():
    g.db = connect(client)


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, "db", None)
    if db is not None:
        pass  # TODO: close connection

heroku = Heroku(app)
