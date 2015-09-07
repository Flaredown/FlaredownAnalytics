from flask_restful import Resource


class TreatmentAPI(Resource):
    def get(self, name):
        return "Bit of the {}?".format(name)
