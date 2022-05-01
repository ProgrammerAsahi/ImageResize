from flask import Flask, request, abort
from rq.job import Job
from RedisConfig import redisConnect, redisQueue
from Image import getSize, resize
from os.path import *
from os import listdir
from log import LogLevel, writeLog
app = Flask(__name__)

'''
Name : Get Image Size API
Description: Get the size of a given image
Parameters: imagePath (Required)
Example: curl -X GET http://127.0.0.1:5000/imageapi?imagePath=/ImageResize/images/CogentLabs.jpg
'''
@app.route('/imageapi', methods=['GET'])
def getImageSizeAPI():
    # When the required parameter - imagePath is not provided
    if 'imagePath' not in request.args:
        return {
            "Result": "Does not specify imagePath parameter. Image request is invalid."
        }, 400
    imagePath = request.args['imagePath']
    # When the given imagePath does not exist
    if not exists(imagePath):
        message = "Image file does not exist."
        writeLog(message, LogLevel.Error)
        return {
            "Width": -1,
            "Height": -1,
            "Result": message
        }, 400
    # When the given imagePath is not a file
    if not isfile(imagePath):
        message = "The given image path is not a file."
        writeLog(message, LogLevel.Error)
        return {
            "Width": -1,
            "Height": -1,
            "Result": message
        }, 400
    # When the imagePath is valid, will put a new task into Redis Queue
    job = redisQueue.enqueue(getSize, imagePath)
    message = f"Task: Get the size of image [{imagePath}] has been put into queue"
    writeLog(message, LogLevel.Ok)
    return {
        "Result": message,
        "jobId": job.id
    }, 200

'''
Name : Resize Image API
Description: Resize a given image or a given batch of images to 100*100pt thumbnail
Parameters: imagePath (Required)
Example: curl -X POST http://127.0.0.1:5000/imageapi?imagePath=/ImageResize/images/CogentLabs.jpg
'''
@app.route('/imageapi', methods=['POST'])
def resizeImageAPI():
    # When the required parameter - imagePath is not provided
    if 'imagePath' not in request.args:
        return {
            "Result": "Does not specify imagePath parameter. Image request is invalid."
        }, 400
    imagePath = request.args['imagePath']
    # When the given imagePath does not start with /ImageResize/images
    if not imagePath.startswith("/ImageResize/images"):
        message = "Invalid image path. The path should starts with [/ImageResize/images]."
        writeLog(message, LogLevel.Error)
        return {
            "Resize": False,
            "Message": message
        }, 400
    # When the given imagePath does not exist
    if not exists(imagePath):
        message = "Image file does not exist"
        writeLog(message, LogLevel.Error)
        return {
            "Resize": False,
            "Message": message
        }, 400
    # When the given imagePath is a file
    if isfile(imagePath):
        # Put a new task into Redis Queue
        job = redisQueue.enqueue(resize, imagePath)
        message = f"Task: Resize image [{imagePath}] has been put into queue"
        writeLog(message, LogLevel.Ok)
        return {
            "Result": message,
            "jobId": job.id
        }, 200
    # When the given imagePath is a directory
    else:
        writeLog(f"Current path [{imagePath}] is a directory. All the images under this directory will be resized.", LogLevel.Ok)
        if not imagePath.endswith("/"):
            imagePath += "/"
        
        paths = listdir(imagePath)
        taskCount = 0
        for item in paths:
            item = imagePath + item
            if isdir(item):
                writeLog(f"Current item [{item}] is a directory, will skip.", LogLevel.Ok)
                continue
            else:
                # Each image will be a seperate task and be put into Redis Queue
                redisQueue.enqueue(resize, item)
                taskCount += 1
                writeLog(f"Task: Resize image [{item}] has been put into queue", LogLevel.Ok)
        
        message = f"Processed [{taskCount}] image resizing tasks. Please directly go to [/ImageResize/images/resized/] to check the results."
        writeLog(message, LogLevel.Ok)
        return {
            "Result": message
        }, 200

'''
Name : Get Result API
Description: Get a task result finished processing by the RQ Workers
Parameters: jobId (Required)
Example: curl -X GET http://127.0.0.1:5000/result?jobId=<the ID of the target job>
'''
@app.route('/result', methods=['GET'])
def getJobResult():
    # When the required parameter - jobId is not provided
    if 'jobId' not in request.args:
        return {
            "Result": "Does not specify jobId parameter. Image request is invalid."
        }, 400
    jobId = request.args['jobId']
    # When the target job does not exist
    try:
        job = Job.fetch(jobId,connection=redisConnect)
    except Exception as e:
        abort(404, descrition=e)
    # When the target job have not finished yet
    if not job.result:
        abort(404, f"Target job with jobId={jobId} cannot find. Please check its status and try again later.")
    
    return job.result

if __name__ == '__main__':
    app.run()