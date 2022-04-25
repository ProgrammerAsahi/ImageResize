from flask import Flask, request
import Image

app = Flask(__name__)

@app.route('/imageapi', methods=['GET'])
def getImageSizeAPI():
    if 'imagePath' not in request.args:
        return {
            "Result": "Does not specify imagePath parameter. Image request is invalid."
        }, 400
    imagePath = request.args['imagePath']
    width, height, message = Image.getSize(imagePath)

    if width != -1 and height != -1:
        return {
            "Result": message,
            "Data": {
                "Width": width,
                "Height": height
            }
        }, 200
    else:
        return {
            "Result": message,
            "Data": {
                "Width": width,
                "Height": height
            }
        }, 400

@app.route('/imageapi', methods=['POST'])
def resizeImageAPI():
    if 'imagePath' not in request.args:
        return {
            "Result": "Does not specify imagePath parameter. Image request is invalid."
        }, 400
    imagePath = request.args['imagePath']
    result, message = Image.resize(imagePath)
    if result:
        return {
            "Result": "Target image have been resized to 100*100pt thumbnail successfully.",
            "Resized Image Path": message
        }, 200
    else:
        return {
            "Result": "Failed to resize the target image.",
            "Error Message": message
        }, 400

    

if __name__ == '__main__':
    app.run()