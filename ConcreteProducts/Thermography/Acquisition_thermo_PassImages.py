import glob
import sys
from os import listdir, makedirs, remove
from os.path import join, exists, basename
from shutil import copyfile
import logging

from Factories.Abstract_factory_and_products import Acquisition

class Acquisition_Thermo(Acquisition):
    """
    This is a replacement class for the Acquisition of the thermography pipeline. It only loads images from a folder and copies them to the Acquired_images folder in the working directory.

    Args:
            Working_directory (str): path to the working directory of the pipeline.
            Image_directory (str): path to the thermography images containing .png or .TIFF files.
    """
    def __init__(self, WorkingDirectory: str, ImageDirectory: str = "") -> None:
        # Loading & saving parameters
        self.Working_directory = WorkingDirectory
        self.Image_directory = ImageDirectory
        self.image_paths = []

        # tuple which contains all file types which will be loaded
        self.filetypes = ('*.png', '*.jpg', '*.tiff', '*.jpeg')
       
        # Setup logger
        self.logger = logging.getLogger(__name__)

    def load_images(self) -> list():
        """
        This function returns a list containing all the image paths from the ImageDirectory.
        """
        if not exists(self.Image_directory):
            self.Image_directory = input("Please enter the path to the folder containing the images:")

            if not exists(self.Image_directory):
                self.logger.error(f"Image directory given does not exist!")
                sys.exit(1)
        
        image_paths = []
        for filetype in self.filetypes:
            image_paths.extend(glob.glob(join(self.Image_directory, filetype)))

        self.image_paths = image_paths

        self.logger.info(f"{__name__} - {len(self.image_paths)} images loaded from {self.Image_directory}") 

        return image_paths

    def save_images(self):
        """
        Copies all the images from the ImageDirectory to the Acquired_images folder in the working directory.
        """
        NewImageDir = join(self.Working_directory, "1.Acquired_images")

        if not exists(NewImageDir):
            makedirs(NewImageDir)
        else:
            # This overwrites already existing results
            for filename in listdir(NewImageDir):
                remove(join(NewImageDir, filename))

        # This overwrites files with the same name
        for image_path in self.image_paths:
            new_image_path = join(NewImageDir,basename(image_path))

            copyfile(image_path,new_image_path)

    def main(self):
        self.load_images()
        self.save_images()

    


   


    

   
