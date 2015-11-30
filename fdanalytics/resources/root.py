from flask_restful import Resource


class RootAPI(Resource):
    def get(self):
        return {"root": "Welcome to the Flaredown analytics API!"}
