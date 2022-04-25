from unittest import result
from flask import Flask
from flask_restful import Resource, Api, reqparse
import Image

app = Flask(__name__)
api = Api(app)

class ImageAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('imagePath', required=True)
        args = parser.parse_args()
        result = Image.getSize(args['imagePath'])

        if result != (-1, -1):
            return {
                "Message": "Get the target image size successfully.",
                "Data": {
                    "Width": result[0],
                    "Height": result[1]
                }
            }, 200
        else:
            return {
                "Message": "Failed to get the target image size. Image request is invalid. Please check the latest log under ./Logs folder for more info.",
                "Data": {
                    "Width": -1,
                    "Height": -1
                }
            }, 400



api.add_resource(ImageAPI, '/imageapi')