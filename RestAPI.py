from flask import Flask, request, abort
from rq.job import Job
from RedisConfig import redisConnect, redisQueue
from Image import getSize, resize

app = Flask(__name__)

@app.route('/imageapi', methods=['GET'])
def getImageSizeAPI():
    if 'imagePath' not in request.args:
        return {
            "Result": "Does not specify imagePath parameter. Image request is invalid."
        }, 400
    imagePath = request.args['imagePath']
    job = redisQueue.enqueue(getSize, imagePath)

    return {
        "Result": f"Task: Get the size of image [{imagePath}] has been put into queue",
        "jobId": job.id
    }, 200

@app.route('/imageapi', methods=['POST'])
def resizeImageAPI():
    if 'imagePath' not in request.args:
        return {
            "Result": "Does not specify imagePath parameter. Image request is invalid."
        }, 400
    imagePath = request.args['imagePath']
    
    job = redisQueue.enqueue(resize, imagePath)
    return {
        "Result": f"Task: Resize image [{imagePath}] has been put into queue",
        "jobId": job.id
    }, 200

@app.route('/result', methods=['GET'])
def getJobResult():
    if 'jobId' not in request.args:
        return {
            "Result": "Does not specify jobId parameter. Image request is invalid."
        }, 400
    jobId = request.args['jobId']
    try:
        job = Job.fetch(jobId,connection=redisConnect)
    except Exception as e:
        abort(404, descrition=e)
    
    if not job.result:
        abort(404, f"Target job with jobId={jobId} cannot find. Please check its status and try again later.")
    
    return job.result


    

if __name__ == '__main__':
    app.run()