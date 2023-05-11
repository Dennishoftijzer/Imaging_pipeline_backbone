import glob
import sys
from os.path import exists, join, splitext, basename
from os import makedirs, listdir, remove
import numpy as np
import imgviz
from PIL import Image, ImageFilter, ImageOps
import matplotlib as plt
import re

from Factories.Abstract_factory_and_products import Preprocess, Acquisition
import logging

class Preprocess_Thermo(Preprocess):
    """
    Preprocessing class for thermography pipeline. Currently, it performs three preprocessing steps:
    1. Converting to grayscale (such that the PIL image only has 1 channel) and a slight median filter blur to remove dead pixels.
    2. Interquirtile range (IQR) outlier removal on pixel intensities.
    3. Equalizing pixel intensities based on pixel mean and std dev.
    
    You can perform any subset of preprocessing steps in any order. Use the preprocess_steps() method to do all the preprocessing steps.
    self.images_dict contains all the PIL images with the original path as key. Keep in mind that these images are overwritten each precprocessing step.
    
     Args:
        WorkingDirectory (str): path to the working directory of the pipeline.
        filter_size (int): Size of PIL median filter in order to remove dead pixels in Preprocess_step1.
    """

    def __init__(self, WorkingDirectory: str, filter_size: int = 3) -> None:
        # Loading & saving parameters
        self.Working_directory = WorkingDirectory
        self.Image_directory = join(WorkingDirectory, '2.IQA_images')
        self.image_paths = []
        self.images_dict = dict()

        # tuple which contains all file types which will be loaded
        self.filetypes = ('*.png', '*.jpg', '*.tiff', '*.jpeg')

        # Filter parameters. Default is 3 pixels.
        if filter_size == None:
            self.filter_size = 3
        else:
            self.filter_size = filter_size

        # Setup logger
        self.logger = logging.getLogger(__name__)

    def load_images(self, collaborator: Acquisition = None):
        """
        This function can be used to load the images before doing a number of preprocessing steps from the client.

        Args: 
            collaborator (optional): Another concrete product which has a load_images() method which returns the image paths (e.g. the empty acquisition module).
                                     When using a collaborator, images can directly be loaded into this module without the acquisition and IQA module.
        """
        try:
            self.image_paths = collaborator.load_images()
            self.Image_directory = collaborator.Image_directory
            self.logger.info(f"{__name__} - Loading images via {collaborator}")
        except AttributeError:
            if not exists(self.Image_directory):
                self.logger.info(f"{__name__} - {self.Image_directory} does not exist.")
                self.Image_directory = input("Please enter the path to the folder containing the images:")

            for filetype in self.filetypes:
                self.image_paths.extend(glob.glob(join(self.Image_directory, filetype)))

            if not exists(self.Image_directory):
                self.logger.error(f"Image directory: {self.Image_directory} does not exist!")
                sys.exit(1)
        
        # uip is a list containing all the names of the images without the frequency part. 
        uip = [re.sub("[0-9]+_?[0-9]*Hz", "", basename(s)) for s in self.image_paths]
        
        # This next part checks if there are indeed 3 grayscale images otherwise give Assertionerror
        for composite_image_name in set(uip):

            split_path = re.split('\s\s', composite_image_name)

            corresponding_paths = [s for s in self.image_paths if split_path[0] in s]
            corresponding_paths = [s for s in corresponding_paths if split_path[1] in s]

            try:
                assert len(corresponding_paths) == 3, "number of channels unequal to 3!"
            except AssertionError:
                self.logger.error(f"{__name__} - Number of channels is unequal to 3! Check files: {corresponding_paths}")
                raise

            # Load images and store in dictionary with path key
            for path in corresponding_paths:
                image = Image.open(path)
                self.images_dict[path] = image

        self.logger.info(f"{__name__} - {len(self.images_dict)} images loaded from {self.Image_directory}") 
        return
   
    def mask_array_to_image(self):
        """
        Not implemented in the preprocessing steps
        """
        colormap = imgviz.label_colormap()
        for path, image in self.images_dict.items():
            lbl_pil = image.convert("P")
            lbl_pil.putpalette(colormap.flatten())

            self.images_dict[path] = image
        return

    
    def gray2heat(im):
        """
        Not implemented in the preprocessing steps
        """
        ima = np.asarray(im).copy()
        cmap = plt.get_cmap('magma')
        ima = cmap(im)
        ima = np.delete(ima, 3, 2)
        ima = np.interp(ima, (ima.min(), ima.max()), (-0, +255)).astype('uint8')

        return Image.fromarray(ima)

    def Preprocess_step1(self):
        """
        Slight median filter blur to remove dead pixels.
        """
        for path, image in self.images_dict.items():
            _, file_extenstion = splitext(path)
 
            if type(image) is np.ndarray:
                image = Image.fromarray(image)

            image = ImageOps.grayscale(image)
            im_filtered = image.filter(ImageFilter.MedianFilter(size=self.filter_size))
            self.images_dict[path] = im_filtered

        self.logger.info(f"{__name__} - Preprocess step 1 done! - Slight median blur - No. images: {len(self.images_dict)}") 
        return
    
    def Preprocess_step2(self):
        """
        Interquirtile range (IQR) outlier removal on pixel intensities.
        I think this will also work:
        PIL.ImageOps.autocontrast(image, cutoff=25, ignore=None, mask=None, preserve_tone=False)
        """
        for path, image in self.images_dict.items():

            if type(image) is Image.Image:
                arr = np.asarray(image)
            else:
                arr = image

            Q1 = np.quantile(arr, 0.25)
            Q3 = np.quantile(arr, 0.75)
            IQR = Q3-Q1

            res = arr.copy()
            res[arr > (Q3+IQR*1.5)] = Q3+IQR*1.5
            res[arr <= (Q1-IQR*1.5)] = Q1-IQR*1.5

            self.images_dict[path] = res

        self.logger.info(f"{__name__} - Preprocess step 2 done! - Interquirtile range (IQR) outlier removal - No. images: {len(self.images_dict)}") 
        return

    def Preprocess_step3(self):
        """
        Scaling of pixel intensities.
        """
        for path, image in self.images_dict.items():

            if type(image) is Image.Image:
                arr = np.asarray(image)
            else:
                arr = image

        # PIL.ImageOps.equalize(image, mask=None)
            m = arr.mean()
            sd = arr.std()
            ima = np.interp(arr, (m-sd*2, m+sd*2), (-0, +255))

            self.images_dict[path] = ima

        self.logger.info(f"{__name__} - Preprocess step 3 done! - Pixel intesity scaling - No. images: {len(self.images_dict)}") 
        return

    def save_images(self):
        NewImageDir = join(self.Working_directory, "3.Preprocessed_images")

        if not exists(NewImageDir):
            makedirs(NewImageDir)
        else:
            # This overwrites already existing results
            for filename in listdir(NewImageDir):
                remove(join(NewImageDir, filename))

        for path, image in self.images_dict.items():
            if type(image) == np.ndarray:
                image = Image.fromarray(image.astype(np.uint8))

            image.save(join(NewImageDir, basename(path)))
        return

    def Preprocess_steps(self):
        """
        You can change this to any order or any number of steps.
        """
        self.Preprocess_step1()
        self.Preprocess_step2()
        self.Preprocess_step3()

    def main(self):
        self.load_images()
        self.Preprocess_steps()
        self.save_images()

