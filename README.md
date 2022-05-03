# ReadMe - Xu Li's Assignment

## Get Started
Welcome to this image resizing project. This documentation has all the contents you needed to understand, run and test this project. To have the perfect experiences, please follow this readme step by step. Wish you could have fun!

## Prerequisites
To run this image resizing service successfully, the following prerequisites must be satisfied. Please make sure that you do not miss any of them.
1. A laptop with mainstream OS & terminal installed  
For Windows: Windows Command Prompt  
For Mac OS & Linux: Terminal
2. Has Docker installed  
Run `docker --version` to confirm this  
If you have not installed docker yet, please move here to install their latest stable version - [Docker](https://www.docker.com/).
3. Has Git installed  
Run `git --version` to confirm this  
If you have not installed git yet, please move here to install their latest stable version - [Git](https://git-scm.com/).
4. A tool that could get access to the REST Service Endpoint of this project. At least one of the following tools should be installed:  
4.1 **cURL** - A command line tool that could send web requests and transfer data via terminal. To install cURL, Please move here - [cURL](https://curl.se/).   
4.2 **RESTAPI Testing Software** - An API testing software could help you achieve accessing our APIs as well. Here we suggests to use [Postman](https://www.postman.com/).  
For myself, I choosed Postman as it is straightforward and easy to operate.  
5. A Python IDE that could open & manage this project. And could run the 2 Unit Test files in this project.  
For myself, I choose to use [Visual Studio Code](https://code.visualstudio.com/) with its [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) installed.

## Project Introduction
This project is a backend web application. It provides image size related services - Get the 2D size of an image, or resize any given images to 100×100pt thumbnail.

### Architecture
Image processing could be time-consuming. To support continous and long running image processing ability, this service has been designed as a task queue based application - more specifically, it uses **Redis Queue** to deal with continuous incoming image tasks. To support the running of Redis Queue, obviously **Redis** is necessary as well. To enable the users to interact with this service, the **RESTAPIs** are provided. Last but not least, there should be **workers** as well to continously deal with images and output results to the users.  

Therefore, the whole application is composed by 3 microservices - **RESTAPIs**, **Redis Queue & Workers** and **Redis**. Also, all of them are implemented via **Python**.  

To better manage these microservices seperately, **all of them are containerized** via Docker respectively. The following diagaram demonstrates all the main components and their relationships:  

![Service Architecture](./docimgs/Architecture.jpg)    

As it displays, at the **producer end** of Redis Queue, when service user submits an image request to the RESTAPI, the API will treat it as an image task, and put it into the queue.

On the other hand, at the **consumer end** of the queue, there will be workers handling these image processing tasks. They take those tasks out of the queue, and utilize **image APIs** to process images. Meanwhile, they will write logs to record their behaviors as well.  
When the tasks are done, queue workers will return the result in JSON. Users could either hit the RESTAPI, or directly visit the destination folders, to get their image processing results.  

In addition, to enable the service to read & write image files, the **containers of RESTAPIs & Workers** have been set up to **utilize volumes to mount the image directory in host machines** to both containers. All the images stored under `./images/` folder could be processed by this service.

Similar to log writing as well. The folder `./logs/` is mounted to both containers as well. They could write logs under this folder when they are executing.  

The following diagram could better demonstrate this process:  

![Use Docker Volume to mount files](./docimgs/Volume.jpg)

As the chart above shows, the images & logs writing could reflect the run-time behaviors of this service, which make it become both achievable & monitorable.

### Project Files Overview
1. Directories  
    * **docimgs** - includes all images that are used in this ReadMe  
    * **images** - includes all the images that could be processed by this application
    * **logs** - stores all the logs written by this application while its running
2. Files  
    * **docker-compose.yml** & **Dockerfile** - Recorded detailed configurations of the 3 containers above
    * **Image.py** - Defined all the image APIs that could be utilized by Workers to process images.
    * **log.py** - Defined a log function. Used by RESTAPI & Workers to write logs.
    * **RedisConfig.py** - Set up Redis Server & initialized Redis Queue.
    * **requirements.txt** - Listed all the python module dependencies that 3 containers need to install.
    * **RestAPI.py** - Defined all the REST Endpoints where users could get access to and send image request.  
    * **TestImage.py** - Defined all the unit test functions for testing the methods in Image.py.
    * **TestRestAPI.py** - Defined all the unit test functions for testing the Rest Endpoint methods in RestAPI.py.

### Referenced Libraries
As listed in `./requirements.txt` file, this application references 4 python modules:  
* **Flask** - Provides the web framework & facilitates the REST Endpoints development for this project.
* **Pillow** - Provides necessary image processing APIs. Make it possible for this application to resize images.
* **Redis** - Enables the application to get access to Redis.
* **RQ (Redis Queue)** - Enables the application to utilize Redis Queue.

### RESTAPIs Overview
This application offeres 3 APIs that users could get access to. Their functionalities and usage ways are listed below:
1. Get Image Size API
    * Effect - Request to get the size of a given image
    * HTTP Method - `GET`
    * Parameters - `imagePath` (**Mandatory**)
    * Usage - Hit the following URL via cURL or Postman:
    `http://127.0.0.1:5000/imageapi?imagePath=<Your image path>`  
    The parameter `imagePath` is mandatory. You should specify the absolute path of a image by yourself. Notice that all the image paths should start with `/ImageResize/images/`, **as they are the ones in container, not in your laptop**. The path `/ImageResize/images/*` is equivalent to `./images/*`, on your laptop.   
    * Return - JSON data will be returned. If the request is valid, the API will **return a success message and a jobId** that you could get the result later. Otherwise, it will **return a failure message**.
    * Example - Get the size of example image `CogentLabs.jpg`.  
        * If you want to get the size of your own image, please copy that target image into `./images/` folder. Here we will just use the example image `CogentLabs.jpg`
        * Start the application
        * Open Postman, Select the method as `GET`  
        * Send the following request to this application via Postman:  
    `http://127.0.0.1:5000/imageapi?imagePath=/ImageResize/images/CogentLabs.jpg`  
        * The service returns the following JSON data:  
        ```
        {  
            "Result": "Task: Get the size of image [/ImageResize/images/CogentLabs.jpg] has been put into queue",  
            "jobId": "c99162f2-0b99-4b45-9884-1cc7af3d378d"
        }
        ```
        Notice that you could use the returned `jobId` to further get the processing result from workers. The result could be kept for 500 seconds.

2. Resize Image API
    * Effect - Request to resize a given image or a given batch of images to 100×100pt thumbnail.
    * HTTP Method - `POST`
    * Parameters - `imagePath` (**Mandatory**)
    * Usage - Hit the following URL via cURL or Postman:
    `http://127.0.0.1:5000/imageapi?imagePath=<Your image path>`  
    The parameter `imagePath` is mandatory. You should specify the absolute path of a image or a folder by yourself. Notice that all the image paths should start with `/ImageResize/images/`, **as they are the ones in container, not in your laptop**.The path `/ImageResize/images/*` is equivalent to `./images/*` on your laptop.   
    Also, if you give a single image path, only that target image will be resized. Instead, if you give a directory, all the images under that folder will be resized (**Not recursive**).
    * Return - JSON data will be returned. If the request is valid, the API will **return a success signal and a jobId** that you could get the result later. Otherwise, it will **return a failure message and a failure signal**.
    * Example 1 - Resize the example image `CogentLabs.jpg`.  
        * If you want to resize your own image, please copy that target image into `./image/` folder. Here we will just use the example image `CogentLabs.jpg`
        * Start the application
        * Open Postman, Select the method as `POST`  
        * Send the following request to this application via Postman:  
    `http://127.0.0.1:5000/imageapi?imagePath=/ImageResize/images/CogentLabs.jpg`  
        * The service returns the following JSON data:  
        ```
        {  
            "Result": "Task: Resize image [/ImageResize/images/CogentLabs.jpg] has been put into queue",  
            "jobId": "6f950a07-7eb6-454e-856b-ab2d15d5efd8"  
        }
        ```
        Notice that you could use the returned `jobId` to further get the processing result from workers. The result could be kept for 500 seconds.
        * All the resized images will be put under `./images/resized/` folder. You could also directly go to that folder to check the result.
    * Example 2 - Batch Processing: Resize all the images in a folder
        * If you want to resize your own image batch, please put all images in the same folder, and copy that folder into `./images/` folder. Here, we will just copy the prepared `/Japan/` folder into `./images/` folder. The `/Japan/` folder contains 500 HD images, which were downloaded from **pexels.com**.
        * Start the application
        * Open Postman, Select the method as `POST`  
        * Send the following request to this application via Postman:  
        `http://127.0.0.1:5000/imageapi?imagePath=/ImageResize/images/Japan/`  
        * The service returns the following JSON data:  
        ```
        {
            "Result": "[500] image resizing tasks have been put into queue. Please directly go to [/ImageResize/images/resized/] to check the results."
        }
        ```
        * Move to `./images/resized/` folder, you could see that the resized images are gradually generated by the application.

3. Get Result API
    * Effect - Get the task results that was finished processing by Workers.
    * HTTP Method - `GET`
    * Parameters - `jobId` (**Mandatory**)
    * Usage - Hit the following URL via cURL or Postman:
    `http://127.0.0.1:5000/result?jobId=<Your Own JobID>`  
    The parameter `jobId` is mandatory. You should specify it by utilizing the return results from previous 2 APIs.
    * Return - JSON data will be returned. If the jobId is valid, you will see **the image process result returned by those image functions**. Otherwise, you will see **a failure message complains about the invalid jobId or other errors**.
    * Example - Get the results of previous 2 tasks handling example image `CogentLabs.jpg`.  
        * Start the application
        * Open Postman, Select the method as `GET`  
        * Send the following 2 requests to this application via Postman:  
        `http://127.0.0.1:5000/result?jobId=c99162f2-0b99-4b45-9884-1cc7af3d378d`  
        `http://127.0.0.1:5000/result?jobId=6f950a07-7eb6-454e-856b-ab2d15d5efd8`

        * The service returns the following JSON data respectively:  
        For `jobId=c99162f2-0b99-4b45-9884-1cc7af3d378d`  
        ```
        {  
            "Height": 830,  
            "Result": "Get the size of target image successfully.",  
            "Width": 1996
        } 
        ```  
        The data above display that the worker successfully get the size of our example image `CogentLabs.jpg` - its Height & Width are 830 and 1996 respectively.  
        For `jobId=6f950a07-7eb6-454e-856b-ab2d15d5efd8`
        ```
        {  
            "Message": "/ImageResize/images/resized/CogentLabs_resized.jpg",  
            "Resize": true  
        }
        ```
        The data above display that the worker successfully resized our example image `CogentLabs.jpg` and stored the new one to path `/ImageResize/images/resized/CogentLabs_resized.jpg`. If you step to the folder `./image/resized/`, you will discover the resized image `CogentLabs_resized.jpg`, which is exactly what we want.

You can know more about how to use these 3 APIs in the following 2 sections: Running & Testing.

## Run this Application  
To properly run this app, please follow the detailed instructions below.
### Start the application
Here are the steps to start this application:  
1. Open the command line tool in your OS.
    * For Windows, open **Command Prompt**
    * For Mac OS or Linux, open **Terminal**
2. Find your best place, and pull this project down. Run the following command:  
`git clone https://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@github.com/ProgrammerAsahi/ImageResize.git`  
3. Move to the root directory of this project, should be under `ImageResize` Folder  
4. If this is your first time running this project, please run `docker compose build`. It may cost some time to complete.
5. Run `docker compose up`. If you see the info appears on your terminal like the following one, that means the application is ready:  
```
imageresize-web-1     |  * Serving Flask app 'RestAPI.py' (lazy loading)
imageresize-web-1     |  * Environment: production
imageresize-web-1     |    WARNING: This is a development server. Do not use it in a production deployment.
imageresize-web-1     |    Use a production WSGI server instead.
imageresize-web-1     |  * Debug mode: off
imageresize-web-1     |  * Running on all addresses (0.0.0.0)
imageresize-web-1     |    WARNING: This is a development server. Do not use it in a production deployment.
imageresize-web-1     |  * Running on http://127.0.0.1:5000
imageresize-web-1     |  * Running on http://172.19.0.2:5000 (Press CTRL+C to quit)
imageresize-worker-1  | 08:27:12 Worker rq:worker:e3ca0ea9eb404a85af3c77bb3d0b6311: started, version 1.10.1
imageresize-worker-1  | 08:27:12 Subscribing to channel rq:pubsub:e3ca0ea9eb404a85af3c77bb3d0b6311
imageresize-worker-1  | 08:27:12 *** Listening on default...
imageresize-worker-1  | 08:27:12 Cleaning registries for queue: default
```  
### Send Requests to the application
After the application is ready, it will listen to all the web requests at port 5000. Therefore all the web requests should start with `http://127.0.0.1:5000/`  
As we discussed in previous API section, you are allowed to send web requests to 3 APIs. Here is a summary of them:  
| No. | Name | Endpoint | Http Method | Mandatory Parameters | Effects|
| --- | --- | --- | --- | --- | --- |
| 1 | Get Image Size API | /imageapi | GET | imagePath | Get the size of a image |
| 2 | Resize Image API | /imageapi | POST | imagePath | Resize a given image or a given batch of image |
| 3 | Get Result API | /result | GET | jobId | Get the task results processed by RQ Workers |

For more detailed usage info, please go back to the APIs Overview Section.  

### Stop the Application  
To stop this app, just press `Ctrl + C` for 2 times, then the app will stop.  

## Test this application
Unit Tests are prepared in this project. They are defined in `TestImage.py` & `TestRestAPI.py`. All the REST Endpoints methods & image processing methods are covered by these unit test functions. Also, for testing each method, both valid inputs & invalid inputs are covered. Valid inputs will test whether the target method could behave as expected. Invalid inputs will test whether the target method is armstrong enough, and could handle various exceptions properly.

### Unit Test Cases
Here is a summary of all the unit test cases for testing all the methods in `Image.py` & `RestAPI.py`:  
| Test Case | Target Method | Input | Valid? | Meet Expection?|  
| --- | --- | --- | --- | --- |
| 1 | Image.getSize | Nonexistent imagePath | Invalid | Yes |
| 2 | Image.getSize | imagePath is a directory | Invalid | Yes |
| 3 | Image.getSize | imagePath is a non-image file | Invalid | Yes |
| 4 | Image.getSize | Normal imagePath | Valid | Yes |
| 5 | Image.resize | imagePath is a non-image file | Invalid | Yes |
| 6 | Image.resize | Normal imagePath | Valid | Yes |
| 7 | RestAPI.getImageSizeAPI | a GET Request, imagePath is not provided | Invalid | Yes |
| 8 | RestAPI.getImageSizeAPI | a GET Request, valid imagePath is provided | Valid | Yes |
| 9 | RestAPI.resizeImageAPI | a POST Request, imagePath is not provided | Invalid | Yes |
| 10 | RestAPI.resizeImageAPI | a POST Request, a nonexistent imagePath is provided | Invalid | Yes |
| 11 | RestAPI.resizeImageAPI | a POST Request, a valid imagePath of an image file is provided | Valid | Yes |
| 12 | RestAPI.resizeImageAPI | a POST Request, a valid imagePath of a directory is provided | Valid | Yes |
| 13 | RestAPI.getJobResult | a GET Request, jobId is not provided | Invalid | Yes |
| 14 | RestAPI.getJobResult | a GET Request, jobId is provided, error occurred when fetching target job | Invalid | Yes |
| 15 | RestAPI.getJobResult | a GET Request, jobId is provided, the target job is unfinished | Invalid | Yes |
| 16 | RestAPI.getJobResult | a GET Request, valid jobId is provided, the target job is finished | Valid | Yes |

### Run Unit Tests
To run the unit tests above, here are the steps:
1. Since these unit tests will run on your local machine, please make sure your machine has `Python 3` installed, and has the 4 modules in `./requirements.txt` installed. If not, please install `Python 3` first, and then run `pip install -r ./requirements.txt` to install the 4 modules.  
2. Open this project with your IDE  
3. Step to either `TestImage.py` or `TestRestAPI.py`
4. Hit the **Run** button on your IDE  
5. You could also run these 2 files on your Terminal:  
`python TestImage.py`  
`python TestRestAPI.py`  
They should give you the same result as **Step 4** did.

Here are the running results I got by using Visual Studio Code with Python 3.9 configured:  
For running `TestImage.py`:  
```
PS D:\ImageResize> & "C:/Program Files/WindowsApps/PythonSoftwareFoundation.Python.3.9_3.9.3312.0_x64__qbz5n2kfra8p0/python3.9.exe" d:/ImageResize/TestImage.py
......
----------------------------------------------------------------------
Ran 6 tests in 0.957s

OK
```
For running `TestRestAPI.py`:
```
PS D:\ImageResize> & "C:/Program Files/WindowsApps/PythonSoftwareFoundation.Python.3.9_3.9.3312.0_x64__qbz5n2kfra8p0/python3.9.exe" d:/ImageResize/TestRestAPI.py
..........
----------------------------------------------------------------------
Ran 10 tests in 0.083s

OK
```

Yours should be similar with the results above.

## Future Improvements
As this application was just developed in 7 days, it is definitely imperfect and has a lot of places that could improve. The last part of this ReadMe will discuss about these limitations. And then, regarding these shortcomings, provides some possbie solutions in the future.

### Features Aspect
**Limitation**: This application can only deal with images stored on the local host machine. Also, it requires users to move these images under `./images/` directory. Similarly, for batch processing, currently this application can only support resizing image, other actions are not included. Those images waiting for batch processing are required to put under the same folder. These are obvious limitations to the users.  

**Possible Improvements**: The improved new version should support uploading the image from any location of the file system on users' local machine. Also, it should support dealing with images from the Internet, and from cloud drives, like Google Drive or Dropbox, etc. Same for batch processing, the batch request submitted by users should support images from different locations, and include different actions. Could develop more APIs with different functionalities to realize the improvements above.

### Reliability & Avalibility Aspect
**Limitation** Currently this application is hosted on a single & local machine. If any unexpected incidents happen to the host machine and make it down, this application will become unavailable to the users as well. Such limited reliability is fine when there are just several users of this application. However, if the user number significantly increases, obviouly current solution is not enough.

**Possible Improvements**: To improve the situation, there are several points we can achieve below:  
1. At the application level, there could be more exception handling to cover the corner cases as many as possible. Make sure the app will not get stuck because of any invalid user inputs.
2. At the infrastructrue level, compared to hosting the app on unreliable local machine, we could move it to the cloud and host it on a cloud VM. This is because usually the cloud provider garantees a much higher avalibility than your own local machine. For instance, Azure garantees that their paid VM services would be available **at least 99.9% of the time**. If this is still not enough for us, we could even add more VMs - some are set as primary and others are set as backup. When the primary VMs become unavailable, the backup ones could still keep our service alive.  The number of VMs could be scaled up or down, depending on the workload of our application.  
This solution is more suitable when the workload is evenly distributed in 24 hours of a day. If they are focused on a certain period of a day, however, this solution may not be the best choice. As in low workload period, these VMs are still costing money.
3. If the usages of our application are focused on a certain period, for example in business hours in Japan time, we could use serverless computing on the cloud instead. As one of the PaaS, serverless computing could help us run our application without worring about the underlying infrastructure issue. Because it will be automatically scaled up or down by the cloud provider. Also, serverless computing is usually billed by the actual workload - during spare time when there are no workload on our app, we will not be charged by the cloud provider. Take Azure as an example, we could use Azure Container Apps to run this docker-based application. We will get a much higher availability & reliability, with resonable money cost. 

### Performance Aspect
**Limitation**: Currently, the performance of this application is limited. As it is hosted on a single local machine, the efficiency of handling requests is restricted by the computing power of the local machine. Also, the task data that redis could store is limited by the RAM size of the local machine as well. Therefore, current implemetation of this app cannot support a high loads of requests from lots of users.

**Possible Improvements**: 
We could improve the performance of this application by applying the following points:  
1. To support heavy loads of image requests sent to this application, a **distributed system** is definitely necessary. whether it is about queuing the tasks, or processing images, etc. This is because every single machine has its computing limitations. A distributed system allow the requests to be redirected and processed by several machines together. It could enable our application with much better performances.  
2. Instead of using Redis Queue, a distributed queue system that support much higher loads of data is needed. In this case we could use **Kafka**. As Kafka is able to deal with very high amount of tasks sent by the users. Also, the task data could be kept in a much longer time than redis queue, which enable our users to look up the logs about processing their requests later. Our users could submit their images request at the producer end of Kafka.
3. For processing images, using **Spark** or **Storm** would be a better choice. As both tools are able to process large amount of data in parallel. We could put either of them at the consumer end of Kafka, let them consume Kafka data and quickly resize the images.
4. After getting resized by Spark or Storm, we still need a distributed file system to store those large amount of output new images. For example, **Azure Blob Storage** would be an option here.
5. Combined with the cloud solution I mentioned in previous part, we could utilize the 3 components above or their alternative cloud versions, to form a heavy load tolerated & cloud-based image data pipeline, which is exactly the improved version of our application. Again, for IaaS part, we could scale up and down by adding or deleting computing resources from the VM pool. For PaaS part, the scale up & down could be done automatically by the cloud provider.
6. Moreover, to futher improve the performance of our application and reduce service latency, we could deploy our services to different regions according to our users' geographic distribution. Requests submitted by users in different places would be redirected to the nearest resource node and get processed.

### Monitoring Aspects
**Limitations**: The current solution of this application provided basic logs when executing tasks. However, the log content is simple, which only provides us limited health info of this application. Moreover, we are lack of other monitoring tools as well.

**Possible Improvements**:
The monitoring could be improved via several ways below:
1. More organized, and useful contents of the logs. This would not only provide us more useful health info, but facilitate us to query these logs better.  
2. A conveninent tool to query & manage logs. E.g. **Splunk** would be a great option.  
3. A service health related metrics collector. E.g. **Prometheus** would be a great choice.
4. A health dashboard that could visualize the health metrics and provide us with more straightforward health info. E.g. **Datadog**, **Azure Data Explorer**.



