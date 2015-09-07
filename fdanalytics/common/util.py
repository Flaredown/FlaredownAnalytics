import json
from bson import json_util


def to_json(x):
    return json.dumps(x, default=json_util.default)
