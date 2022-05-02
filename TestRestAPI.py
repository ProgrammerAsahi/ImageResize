import unittest
from unittest import mock
from RestAPI import app
from json import loads
from uuid import uuid4
from os.path import dirname, realpath

class Job():
    def __init__(self, id=uuid4(),result="finished") -> None:
            self.id = id
            self.result = result

class TestRestAPIMethods(unittest.TestCase):
    # set up the app client used by the unit test functions below
    def setUp(self):
        self.client = app.test_client()
    # Mock Function - Mock the output of redisQueue.enqueue
    def mockedRedisQueueEnqueue(functionName, imagePath):
        return Job()
    # Mock Function - Mock exception thrown when executing Job.fetch
    def mockedFetchJobWithErrorOccurred(jobId, connection):
        raise Exception("The target job does not exist")
    # Mock Function - Mock fetching an unfinished job
    def mockedFetchUnfinishedJob(jobId, connection):
        return Job(result=None)
    # Mock Function - Mock fetching a finished job
    def mockedFetchFinishedJob(jobId, connection):
        return Job()

    # Test the RestAPI.getImageSizeAPI method without passing in the required imagePath parameter 
    def testGetImageSizeAPIWithoutImagePath(self):
        response = self.client.get('/imageapi')
        result = loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("Result" in result)
        self.assertTrue("Does not specify imagePath parameter" in result["Result"])
    # Test the RestAPI.getImageSizeAPI method with imagePath parameter passing in
    @mock.patch('rq.Queue.enqueue', side_effect=mockedRedisQueueEnqueue)
    def testGetImageSizeAPIWithValidImagePath(self, mock_get):
        currDir = dirname(realpath(__file__))
        imagePath = currDir + "/images/CogentLabs.jpg"
        response = self.client.get('/imageapi', query_string={
            "imagePath": imagePath
            })
        result = loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Result" in result)
        self.assertTrue("jobId" in result)
        self.assertTrue("has been put into queue" in result["Result"])
    # Test the RestAPI.resizeImageAPI method without passing in the required imagePath parameter
    def testResizeImageAPIWithoutImagePath(self):
        response = self.client.post('/imageapi')
        result = loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("Result" in result)
        self.assertTrue("Does not specify imagePath parameter" in result["Result"])
    # Test the RestAPI.resizeImageAPI method, when imagePath does not exist
    def testResizeImageAPIWithNonexistentImagePath(self):
        currDir = dirname(realpath(__file__))
        imagePath = currDir + "/images/12345.jpg"
        response = self.client.post('/imageapi', query_string={
            "imagePath": imagePath
            })
        result = loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("Resize" in result)
        self.assertTrue("Message" in result)
        self.assertFalse(result["Resize"])
        self.assertTrue("Image file does not exist" in result["Message"])
    # Test the RestAPI.resizeImageAPI method, when the imagePath is a valid image file path
    @mock.patch('rq.Queue.enqueue', side_effect=mockedRedisQueueEnqueue)
    def testResizeImageAPIWithValidImageFilePath(self, mock_post):
        currDir = dirname(realpath(__file__))
        imagePath = currDir + "/images/CogentLabs.jpg"
        response = self.client.post('/imageapi', query_string={
            "imagePath": imagePath
            })
        result = loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Result" in result)
        self.assertTrue("jobId" in result)
        self.assertTrue("has been put into queue" in result["Result"])
    # Test the RestAPI.resizeImageAPI method, when the imagePath is a valid directory path
    @mock.patch('rq.Queue.enqueue', side_effect=mockedRedisQueueEnqueue)
    def testResizeImageAPIWithValidImageDirectoryPath(self, mock_post):
        currDir = dirname(realpath(__file__))
        imagePath = currDir + "/images/"
        response = self.client.post('/imageapi', query_string={
            "imagePath": imagePath
            })
        result = loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Result" in result)
        self.assertTrue("image resizing tasks" in result["Result"])
    # Test the RestAPI.getJobResult method without passing in the required jobId parameter 
    def testGetJobResultAPIWithoutJobId(self):
        response = self.client.get('/result')
        result = loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("Result" in result)
        self.assertTrue("Does not specify jobId parameter" in result["Result"])
    # Test the RestAPI.getJobResult method, when error occurred while fetching target job
    @mock.patch('rq.job.Job.fetch', side_effect=mockedFetchJobWithErrorOccurred)
    def testGetJobResultAPIWithErrorsOccurred(self, mock_get):
        response = self.client.get('/result', query_string={
            "jobId": uuid4()
            })
        result = loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertTrue("Result" in result)
        self.assertTrue("An error occured" in result["Result"])
    # Test the RestAPI.getJobResult method, when target job has not finished yet
    @mock.patch('rq.job.Job.fetch', side_effect=mockedFetchUnfinishedJob)
    def testGetJobResultAPIWithJobUnfinished(self, mock_get):
        response = self.client.get('/result', query_string={
            "jobId": uuid4()
            })
        result = loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertTrue("Result" in result)
        self.assertTrue("cannot find" in result["Result"])
    # Test the RestAPI.getJobResult method, when jobId is valid
    @mock.patch('rq.job.Job.fetch', side_effect=mockedFetchFinishedJob)
    def testGetJobResultAPIWithValidJobId(self, mock_get):
        response = self.client.get('/result', query_string={
            "jobId": uuid4()
            })
        result = loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Result" in result)
    

if __name__ == '__main__':
    unittest.main()
    
