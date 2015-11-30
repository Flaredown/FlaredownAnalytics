from flask import Flask, Blueprint, g
from flask_restful import Api
from flask.ext.heroku import Heroku
from werkzeug.contrib.fixers import ProxyFix
from .common.db import configure_client, connect
from .resources.root import RootAPI
from .resources.condition import ConditionListAPI
from .resources.entry import EntryAPI, EntryListAPI
from .resources.segment import SegmentAPI
from .resources.symptom import SymptomListAPI
from .resources.treatment import TreatmentAPI, TreatmentListAPI
from .resources.user import UserAPI


app = Flask(__name__)
app.config.from_pyfile("../config.py")
app.wsgi_app = ProxyFix(app.wsgi_app)

client = configure_client(app.config)
db = connect(client)

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


@app.before_request
def before_request():
    g.db = connect(client)


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, "db", None)
    if db is not None:
        pass  # TODO: close connection

heroku = Heroku(app)
