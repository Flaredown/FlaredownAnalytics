import os
from flask import Flask, Blueprint, g
from flask_restful import Api
from flask.ext.pymongo import PyMongo
from werkzeug.contrib.fixers import ProxyFix
from .resources.root import RootAPI
from .resources.condition import ConditionListAPI
from .resources.entry import EntryAPI, EntryListAPI
from .resources.segment import SegmentAPI
from .resources.symptom import SymptomListAPI
from .resources.treatment import TreatmentAPI, TreatmentListAPI
from .resources.user import UserAPI


class Config(object):
    pass


class HerokuConfig(Config):
    MONGO_HOST = os.environ.get("MONGO_HOST")
    MONGO_PORT = os.environ.get("MONGO_PORT")
    MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
    MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")


mongo = PyMongo()


def create_app(config_filename):
    app = Flask(__name__)

    if os.environ.get("HEROKU"):
        app.config.from_object(HerokuConfig)
    else:
        app.config.from_pyfile("../config.py")

    app.wsgi_app = ProxyFix(app.wsgi_app)

    api_bp = Blueprint("api", __name__)
    api = Api(api_bp)

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

    mongo.init_app(app)

    return app


app = create_app("../config.py")


@app.before_request
def before_request():
    g.db = mongo.db


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, "db", None)
    if db is not None:
        pass  # TODO: close connection
