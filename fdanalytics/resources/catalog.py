from flask import g
from flask_restful import Resource
from ..common.util import ignore_case


class CatalogListAPI(Resource):
    def get(self):
        return {
            "catalogs": g.db.entries.distinct("catalogs")
        }


class CatalogAPI(Resource):
    def get(self, catalog_name):
        # TODO: len(distinct) won't scale well, use aggregation pipeline instead

        return {
            "catalog": {
                "name": catalog_name.lower(),
                "num_entries": g.db.entries.count({"catalogs": ignore_case(catalog_name)}),
                "num_users": len(g.db.entries.distinct("user_id", {"catalogs": ignore_case(catalog_name)}))
            }
        }
