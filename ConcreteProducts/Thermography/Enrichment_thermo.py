import glob
import sys
from os.path import exists, join, basename
from os import makedirs, listdir, remove
import numpy as np
from PIL import Image
import re

from sklearn.decomposition import PCA

from Factories.Abstract_factory_and_products import Acquisition, Enrichment
import logging

class Enrichment_Thermo(Enrichment):
    """
    Enrichment class for thermography pipeline.

    This will layer three grayscale images into one RGB composite image. The name of the images must be as follows:

    <identifier> [0-9]+_?[0-9]*Hz <identifier> .filetype

    Where, <identifier> can be any name given to the images. The frequency part must be seperated by a space character. filetype can be any filetype in self.filetypes.

    Args:
        WorkingDirectory (str): path to the working directory of the pipeline.
    """

    def __init__(self, WorkingDirectory) -> None:
        # Loading & saving parameters
        self.Working_directory = WorkingDirectory
        self.Image_directory = join(WorkingDirectory, '3.Preprocessed_images')
        self.image_paths = []
        self.images_dict = {}
        self.composites_im_dict = {}

        # tuple which contains all file types which will be loaded
        self.filetypes = ('*.png', '*.jpg', '*.tiff', '*.jpeg')

        # Filter parameters
        self.filter_size = 3

        # Setup logger
        self.logger = logging.getLogger(__name__)

    def load_images(self, collaborator: Acquisition = None):
        """
        This function can be used to load the images before the enrichment.

        Args: 
            collaborator (optional): Another concrete product which has a load_images() method which returns the image paths (e.g. the empty acquisition module).
                                     When using a collaborator, images can directly be loaded into this module without the acquisition module.
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
        # The regex will match and remove e.g. 1Hz or 0_01Hz in the filenames.
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

    def merge_PCA(self):
        """
        This function was an idea to make sure the output of the enrichment module is always a 3 channel RGB image. It uses PCA to make sure the output image always has 3 images. 
        It is not used in the main function and is not part of the pipeline.
        """
        # This will match also e.g. 1Hz or 0_01Hz
        uip = [re.sub("[0-9]+_?[0-9]*Hz", "", basename(s)) for s in list(self.images_dict.keys())]

        for composite_image_name in set(uip):
            split_path = re.split('\s\s', composite_image_name)

            reObj = re.compile(f"{split_path[0]} [0-9]+_?[0-9]*Hz {split_path[1]}")
    
            images = []
            for path, image in self.images_dict.items():
                if(reObj.match(basename(path))):
                    images.append(image)
          
            res = [np.asarray(arr).flatten() for arr in images]
            res = np.stack(res, axis = 1)

            # Tried to do PCR in order to reduce random amount of channels to 3 channels: RGB.
            pca = PCA(n_components=3)
            pca_arr = pca.fit_transform(res)

            print(pca_arr.shape)
            print(pca.explained_variance_ratio_)
            print(pca.singular_values_)

            # Really bad implementation, need to fix
            MergedImage_arr_r = np.interp(pca_arr[:,0], (pca_arr[:,0].min(), pca_arr[:,0].max()), (-0, +255)).astype('uint8')
            MergedImage_arr_g = np.interp(pca_arr[:,1], (pca_arr[:,1].min(), pca_arr[:,1].max()), (-0, +255)).astype('uint8')
            MergedImage_arr_b = np.interp(pca_arr[:,2], (pca_arr[:,2].min(), pca_arr[:,2].max()), (-0, +255)).astype('uint8')

            MergedImage_arr = np.dstack((MergedImage_arr_r.reshape((512,640)), MergedImage_arr_g.reshape((512,640)), MergedImage_arr_b.reshape((512,640))))

            self.composites_im_dict[composite_image_name] = Image.fromarray(MergedImage_arr)       
        return
    
    def enrich(self):
        """
        This function merges the 3 grayscale images to one RGB image.
        """
        # uip is a list containing all the names of the images without the frequency part. 
        # The regex will match and remove e.g. 1Hz or 0_01Hz in the filenames.
        uip = [re.sub("[0-9]+_?[0-9]*Hz", "", basename(s)) for s in list(self.images_dict.keys())]

        # uip is converted to a set in order to remove duplicates.
        for composite_image_name in set(uip):
            split_path = re.split('\s\s', composite_image_name)

            corresponding_paths = [s for s in self.image_paths if split_path[0] in s]
            corresponding_paths = [s for s in corresponding_paths if split_path[1] in s]

            # This regex will match the 3 different frequeny measurements but is much slower than the list comprehension above
            # reObj = re.compile(f"{split_path[0]} [0-9]+_?[0-9]*Hz {split_path[1]}")
    
            images = [self.images_dict.get(key) for key in corresponding_paths]
                
            self.composites_im_dict[composite_image_name] = Image.merge('RGB', images)

        
        self.logger.info(f"{__name__} - {len(self.images_dict)} grayscale images merged to {len(self.composites_im_dict)} RGB images!") 
        return


    def save_images(self):
        NewImageDir = join(self.Working_directory, "4.Enrichment_images")

        if not exists(NewImageDir):
            makedirs(NewImageDir)
        else:
            # This overwrites already existing results
            for filename in listdir(NewImageDir):
                remove(join(NewImageDir, filename))

        for composite_image_name, image in self.composites_im_dict.items():

            # Replace the double white space with a single space character for saving
            img_name = re.sub("  ", " ", composite_image_name)

            image.save(join(NewImageDir, img_name))
        return


    def main(self):
        self.load_images()
        self.enrich()
        self.save_images()
        return

