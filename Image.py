from PIL import Image
from PIL import UnidentifiedImageError
from log import LogLevel, writeLog
from os.path import *

# This method Return the 2D sizes of a given image.
# If the path does not exist, or the path is not a file, or the file is not an image, the method will all return (-1, -1)
def getSize(imagePath: str):
    # When the given imagePath does not exist
    if not exists(imagePath):
        message = "Image file does not exist."
        writeLog(message, LogLevel.Error)
        return { "Width": -1, "Height": -1, "Result": message}
     # When the given imagePath is not a file
    if not isfile(imagePath):
        message = "The given image path is not a file."
        writeLog(message, LogLevel.Error)
        return { "Width": -1, "Height": -1, "Result": message}
    try:
        img = Image.open(imagePath)
        width, height = img.size
        img.close()
        message = "Get the size of target image successfully." 
        writeLog(message, LogLevel.Ok)
        return {"Width": width, "Height": height, "Result": message}
    except UnidentifiedImageError:
        message = "The given image path is not a valid image format"
        writeLog(message, LogLevel.Error)
        return {"Width": -1, "Height": -1, "Result": message}

# This method resizes the given images to 100*100 px thumbnails
# If resizes successfully, the method will return True; otherwise, the method will return False
def resize(imagePath: str):
    try:
        img = Image.open(imagePath)
        img.thumbnail((100, 100))
        fileName = basename(imagePath)
        currDir = dirname(realpath(__file__))
        savedDirectory = currDir + "/images/resized/"
        root, ext = splitext(fileName)
        resizedImageName = savedDirectory + root + "_resized" + ext
        img.save(resizedImageName)
        writeLog(f"Successfully generated the resized image [{resizedImageName}].", LogLevel.Ok)
        return {"Resize": True, "Message": resizedImageName}
    except UnidentifiedImageError:
        message = "The given image path is not a valid image format"
        writeLog(message, LogLevel.Error)
        return {"Resize": False, "Message": message}