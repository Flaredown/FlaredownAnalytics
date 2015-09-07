import json
from pymongo import MongoClient


if __name__ == "__main__":
    client = MongoClient("mongodb://localhost:27017/")
    db = client.test_db
    entries = db.entries

    entries.remove()

    with open("dump.json") as f:
        couch_entries = [row["doc"] for row in json.load(f)["rows"]]

        entries.insert_many(couch_entries)

    results = entries.distinct("treatments.name")

    print(list(results))
    # print(entries.find_one())

    eg = {
        'treatments': [{'quantity': None, 'unit': None, 'name': None}],
        '_id': 'ecfa13e70e9f40208a5c3ec4786b8884',
        'notes': '',
        'scores': [{'value': None, 'name': None}],
        'triggers': [],
        'catalogs': ['hbi'],
        'responses': [
            {'value': 2.0, 'catalog': 'hbi', 'name': 'general_wellbeing'},
            {'value': 1.0, 'catalog': 'hbi', 'name': 'ab_pain'},
            {'value': 4.0, 'catalog': 'hbi', 'name': 'stools'},
            {'value': 1.0, 'catalog': 'hbi', 'name': 'ab_mass'},
            {'value': 0.0, 'catalog': 'hbi', 'name': 'complication_arthralgia'},
            {'value': 1.0, 'catalog': 'hbi', 'name': 'complication_uveitis'},
            {'value': 1.0, 'catalog': 'hbi', 'name': 'complication_erythema_nodosum'},
            {'value': 1.0, 'catalog': 'hbi', 'name': 'complication_aphthous_ulcers'},
            {'value': 0.0, 'catalog': 'hbi', 'name': 'complication_anal_fissure'},
            {'value': 0.0, 'catalog': 'hbi', 'name': 'complication_fistula'},
            {'value': 1.0, 'catalog': 'hbi', 'name': 'complication_abscess'}
        ],
        'date': '2014-11-21',
        'user_id': '8',
        '_rev': '1-ea84d9ca1a1b75660044d1551c7b037d'
    }

    results = entries.aggregate([
        {
            "$unwind": "$conditions"
        },
        {
            "$group": {
                "_id": {
                    "user_id": "$user_id",
                    "sex": "$settings.sex"
                },
                "count": {"$sum": 1},
                "conditions": {"$addToSet": "$conditions"}
            }
        },
        {
            "$unwind": "$conditions"
        },
        {
            "$group": {
                "_id": {
                    "sex": "$_id.sex",
                    "condition": "$conditions"
                },
                "count": {"$sum": 1}
            }
        }
    ])

    print(list(results))
