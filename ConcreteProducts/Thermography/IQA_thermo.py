import glob
import sys
from os import listdir, makedirs, remove
from os.path import join, exists, basename
import logging
from brisque import BRISQUE
from shutil import copyfile
import matplotlib.pyplot as plt
import re


from Factories.Abstract_factory_and_products import Acquisition, IQA

class IQA_Thermo(IQA):
    """
    This is the Image Quality Assessment (IQA) class for the thermography pipeline. It calculates the BRISQUE score of the acquired 
    grayscale images in order to assess which images are of sufficient quality. 3 grayscale (measurements with different frequency) form
    1 composite RGB image. In the enrichment step, the images are formed into an RGB image. Only when all 3 grayscale images are deemed
    of sufficient quality, the images will proceed to the preprocessing step.

    The name of the images must be as follows:

    <identifier> [0-9]+_?[0-9]*Hz <identifier> .filetype

    Where, <identifier> can be any name given to the images. The frequency part must be seperated by a space character. filetype can be any filetype in self.filetypes.

    Args:
        WorkingDirectory (str): path to the working directory of the pipeline.
        BrisqueThreshold (int): BRISQUE score threshold. Images with a score lower than the threshold are deemed sufficient quality.
    """

    def __init__(self, WorkingDirectory: str, BrisqueThreshold: int = 70) -> None:
        # Loading & saving parameters
        self.Working_directory = WorkingDirectory
        self.Image_directory = join(WorkingDirectory, '1.Acquired_images')
        self.image_paths = []

        # tuple which contains all file types which will be loaded
        self.filetypes = ('*.png', '*.jpg', '*.tiff', '*.jpeg')

        # Brisque score threshold. image[score > treshold] => Discard
        self.brisque_threshold = BrisqueThreshold

        # Setup logger
        self.logger = logging.getLogger(__name__)

    def load_images(self, collaborator: Acquisition = None):
        """
        This function can be used to load the images before doing the IQA.

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

        self.logger.info(f"{__name__} - {len(self.image_paths)} images loaded from {self.Image_directory}") 
        return

    def Asses(self):
        """
        This function is used to determine which images have sufficient quality in order to proceed in the pipeline.
        The quality of an image is determined by the BRISQUE score:

        (see original paper for more detail: A. Mittal, A. K. Moorthy and A. C. Bovik, "No-Reference Image Quality Assessment in the Spatial Domain" 
        in IEEE Transactions on Image Processing, vol. 21, no. 12, pp. 4695-4708, Dec. 2012, doi: 10.1109/TIP.2012.2214050.)

        Each thermography image has 3 frequency measurements. Only when all 3 grayscale frequency measurements have sufficient quality,
        the images can proceed.
        """
        # Brisque object from pybrisque package (https://pypi.org/project/pybrisque/) to calculate brisque score.
        brisq = BRISQUE()
        
        self.logger.info(f"{__name__} - Assessing the images..., images with a BRISQUE score lower than {self.brisque_threshold} will pass")

        self.composite_ls = []

        # uip is a list containing all the names of the images without the frequency part.
        uip = [re.sub("[0-9]+_?[0-9]*Hz", "", basename(s)) for s in self.image_paths]

        # uip is converted to a set in order to remove duplicates.
        for composite_image_name in set(uip):

            # Each composite image will have a dictionary with its name, the grayscale image paths, 
            # BRISQUE scores, a bool whether each individual image passed the threshold and lastly a bool wether all three images have passed. 
            composite_dict = {}

            composite_dict["composite_name"] = composite_image_name

            split_path = re.split('\s\s', composite_image_name)

            corresponding_paths = [s for s in self.image_paths if split_path[0] in s]
            corresponding_paths = [s for s in corresponding_paths if split_path[1] in s]

            # Check if there are indeed 3 grayscale images, otherwise raise Assertionerror
            try:
                assert len(corresponding_paths) == 3, "number of channels unequal to 3!"
            except AssertionError:
                self.logger.error(f"{__name__} - Number of channels is unequal to 3! Check files: {corresponding_paths}")
                raise

            # Calculate BRISQUE scores
            scores = [brisq.get_score(path) for path in corresponding_paths]

            composite_dict["image_paths"] = corresponding_paths
            composite_dict["scores"] = scores
            composite_dict["passed"] = [True if score < self.brisque_threshold else False for score in scores]
            composite_dict["Composite_pass"] = all(passed == True for passed in composite_dict["passed"])

            self.composite_ls.append(composite_dict)

        no_img_passed = sum([sum(x['passed']) for x in self.composite_ls])
        self.logger.info(f"{__name__} - Calculated {len(self.image_paths)} BRISQUE scores, {no_img_passed} of {len(self.image_paths)} images passed the threshold, ")

        # Composite images will only pass when the three grayscale images pass the BRISQUE threshold
        self.logger.info(f"{__name__} - {sum([x['Composite_pass'] for x in self.composite_ls])} of {len(self.composite_ls)} composite images passed")
        return

    def plot_histogram(self):
        """
        This function can be used in order to gain insight in the distribution of BRISQUE scores by plotting a histogram.
        """
        brisque_score_ls = []
        for composite_dict in self.composite_ls:
            brisque_score_ls.extend(composite_dict["scores"])

        fig = plt.figure()
        ax = fig.add_subplot(111)

        y,x, _ = ax.hist(brisque_score_ls, bins = 100, edgecolor='black', label='Scores')
        ax.vlines(70,0,1.2*y.max(), colors='red', label='Threshold')
        ax.set_xlabel("Brisque score")
        ax.set_ylabel("No. of images")
        ax.set_title("Histogram of BRISQUE scores \n Lower score than threshold will pass")
        ax.legend(loc = 'upper right')

        fig.show()
        plt.show()
        return

    def save_images(self):
        """
        This method is used to save the "good quality" images. Only when all 3 images have passed, they proceed to preprocessing.
        """
        NewImageDir = join(self.Working_directory, "2.IQA_images")

        if not exists(NewImageDir):
            makedirs(NewImageDir)
        else:
            # This overwrites already existing results
            for filename in listdir(NewImageDir):
                remove(join(NewImageDir, filename))

        for composite_dict in self.composite_ls:
            if composite_dict["Composite_pass"] == True:
                for path in composite_dict["image_paths"]:
                    new_image_path = join(NewImageDir,basename(path))

                    copyfile(path,new_image_path)

    def main(self):
        self.load_images()
        self.Asses()
        self.save_images()