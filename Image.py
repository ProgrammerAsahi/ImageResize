from PIL import Image
from PIL import UnidentifiedImageError
from os.path import *

# This method Return the 2D sizes of a given image.
# If the path does not exist, or the path is not a file, or the file is not an image, the method will all return (-1, -1)
def getSize(imagePath: str) -> tuple:
    if not exists(imagePath):
        return -1, -1, "Image file does not exist"
    
    if not isfile(imagePath):
        return -1, -1, "The given image path is not a file"
    try:
        img = Image.open(imagePath)
        width, height = img.size
        img.close()
        return width, height, "Get the size of target image successfully."
    except UnidentifiedImageError:
        return -1, -1, "The given image path is not a valid image format"

# This method resizes the given images to 100*100 px thumbnails
# If resizes successfully, the method will return True; otherwise, the method will return False
def resize(imagePath: str) -> tuple:
    if not exists(imagePath):
        return False, "Image file does not exist"
    
    if not isfile(imagePath):
        return False, "The given image path is not a file"
    try:
        img = Image.open(imagePath)
        img.thumbnail((100, 100))
        root, ext = splitext(imagePath)
        resizedImageName = root + "_resized" + ext
        img.save(resizedImageName)
        return True, resizedImageName
    except UnidentifiedImageError:
        return False, "The given image path is not a valid image format"