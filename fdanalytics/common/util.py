import json
import re
from bson import json_util


def ignore_case(s):
    return re.compile("^" + s + "$", re.IGNORECASE)


def safe_index(list, i, default_value=None):
    try:
        el = list[i]
    except IndexError:
        el = default_value

    return el


def to_json(x):
    return json.dumps(x, default=json_util.default)
