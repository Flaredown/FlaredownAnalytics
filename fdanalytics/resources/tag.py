from flask import g
from flask_restful import Resource
from ..common.util import ignore_case


class TagListAPI(Resource):
    def get(self):
        return {
            "tags": g.db.entries.distinct("tags")
        }


class TagAPI(Resource):
    def get(self, tag_name):
        # TODO: len(distinct) won't scale well, use aggregation pipeline instead

        return {
            "tag": {
                "name": tag_name.lower(),
                "num_entries": g.db.entries.count({"tags": ignore_case(tag_name)}),
                "num_users": len(g.db.entries.distinct("user_id", {"tags": ignore_case(tag_name)}))
            }
        }
