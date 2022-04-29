from asyncore import write
from PIL import Image
from PIL import UnidentifiedImageError
from log import LogLevel, writeLog
from os.path import *

# This method Return the 2D sizes of a given image.
# If the path does not exist, or the path is not a file, or the file is not an image, the method will all return (-1, -1)
def getSize(imagePath: str):
    if not exists(imagePath):
        message = "Image file does not exist."
        writeLog(message, LogLevel.Error)
        return toJSON(-1, -1, message)
    
    if not isfile(imagePath):
        message = "The given image path is not a file."
        writeLog(message, LogLevel.Error)
        return toJSON(-1, -1, message)
    try:
        img = Image.open(imagePath)
        width, height = img.size
        img.close()
        message = "Get the size of target image successfully." 
        writeLog(message, LogLevel.Ok)
        return toJSON(width, height, message)
    except UnidentifiedImageError:
        message = "The given image path is not a valid image format"
        writeLog(message, LogLevel.Error)
        return toJSON(-1, -1, message)

# This method resizes the given images to 100*100 px thumbnails
# If resizes successfully, the method will return True; otherwise, the method will return False
def resize(imagePath: str):
    if not exists(imagePath):
        message = "Image file does not exist"
        writeLog(message, LogLevel.Error)
        return toJSON2(False, message)
    
    if not isfile(imagePath):
        message = "The given image path is not a file"
        writeLog(message, LogLevel.Error)
        return toJSON2(False, message)
    try:
        img = Image.open(imagePath)
        img.thumbnail((100, 100))
        root, ext = splitext(imagePath)
        resizedImageName = root + "_resized" + ext
        img.save(resizedImageName)
        writeLog(f"Successfully generated the resized image [{resizedImageName}].", LogLevel.Ok)
        return toJSON2(True, resizedImageName)
    except UnidentifiedImageError:
        message = "The given image path is not a valid image format"
        writeLog(message, LogLevel.Error)
        return toJSON2(False, message)

def toJSON(width: int, height: int, result: str):
    return {
        "Width": width,
        "Height": height,
        "Result": result
    }

def toJSON2(success: bool, message: str):
    
    success = "Successful" if success else "Failed"
    return {
        "Resize": success,
        "Message": message
    }