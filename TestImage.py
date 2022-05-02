import unittest
from Image import getSize, resize
from os.path import exists, dirname, realpath

class TestImageMethods(unittest.TestCase):
    # Test the Image.getSize method, when imagePath does not exist
    def testGetImageSizeWithNonexistentImagePath(self):
        currDir = dirname(realpath(__file__))
        imagePath = currDir + "/images/12345.jpg"
        result = getSize(imagePath)
        self.assertTrue("Width" in result)
        self.assertTrue("Height" in result)
        self.assertTrue("Result" in result)
        self.assertEqual(result["Width"], -1)
        self.assertEqual(result["Height"], -1)
        self.assertTrue("does not exist" in result["Result"])
    # Test the Image.getSize method, when imagePath is a directory
    def testGetImageSizeWithDirectoryPath(self):
        currDir = dirname(realpath(__file__))
        imagePath = currDir + "/images/"
        result = getSize(imagePath)
        self.assertTrue("Width" in result)
        self.assertTrue("Height" in result)
        self.assertTrue("Result" in result)
        self.assertEqual(result["Width"], -1)
        self.assertEqual(result["Height"], -1)
        self.assertTrue("is not a file" in result["Result"])
    # Test the Image.getSize method, when imagePath is not an image file
    def testGetImageSizeWithNonImagePath(self):
        currDir = dirname(realpath(__file__))
        imagePath = currDir + "/logs/Sample.log"
        result = getSize(imagePath)
        self.assertTrue("Width" in result)
        self.assertTrue("Height" in result)
        self.assertTrue("Result" in result)
        self.assertEqual(result["Width"], -1)
        self.assertEqual(result["Height"], -1)
        self.assertTrue("is not a valid image format" in result["Result"])
    # Test the Image.getSize method, when imagePath is a valid image file
    def testGetImageSizeWithValidImagePath(self):
        currDir = dirname(realpath(__file__))
        imagePath = currDir + "/images/CogentLabs.jpg"
        result = getSize(imagePath)
        self.assertTrue("Width" in result)
        self.assertTrue("Height" in result)
        self.assertTrue("Result" in result)
        self.assertGreater(result["Width"], 0)
        self.assertGreater(result["Height"], 0)
    # Test the Image.resize method, when imagePath is not an image file
    def testResizeImageWithNonImagePath(self):
        currDir = dirname(realpath(__file__))
        imagePath = currDir + "/logs/Sample.log"
        result = resize(imagePath)
        self.assertTrue("Resize" in result)
        self.assertTrue("Message" in result)
        self.assertFalse(result["Resize"])
        self.assertTrue("is not a valid image format" in result["Message"])
    # Test the Image.resize method, when imagePath is a valid image file
    def testResizeImageWithValidImagePath(self):
        currDir = dirname(realpath(__file__))
        imagePath = currDir + "/images/CogentLabs.jpg"
        savedImagePath = currDir + "/images/resized/CogentLabs_resized.jpg"
        result = resize(imagePath)
        self.assertTrue("Resize" in result)
        self.assertTrue("Message" in result)
        self.assertTrue(result["Resize"])
        self.assertEqual(result["Message"], savedImagePath)
        self.assertTrue(exists(savedImagePath))

if __name__ == '__main__':
    unittest.main()