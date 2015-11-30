import json
import re
from bson import json_util


def ignore_case(s):
    return re.compile("^" + s + "$", re.IGNORECASE)


def to_json(x):
    return json.dumps(x, default=json_util.default)
