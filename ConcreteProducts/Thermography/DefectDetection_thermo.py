import glob
import sys
from os.path import exists, join, basename
from os import listdir, remove, makedirs
from PIL import Image, ImageFont, ImageDraw
import re

import torch
from torchvision.utils import draw_bounding_boxes
from torchvision.io import read_image
import matplotlib.pyplot as plt
import random

from Factories.Abstract_factory_and_products import Acquisition, DefectDetection
import logging

class DefectDetection_Thermo(DefectDetection):
    """
    Defect detection class for the thermography pipeline. 
    
    The defect detection model uses the detectron2 library and was trained locally on the ARVI PC with a pretrained faster_rcnn_R_50_FPN_1x architecture.
    The output of the training can be found in Imaging_pipeline_backbone\ConcreteProducts\Thermography\Defect_detection_model\training_output.

    The model was exported via torchscript, such that inferance is possible without detectron2 package dependency. See:

    https://detectron2.readthedocs.io/en/latest/tutorials/deployment.html    (very limited documentation)

    and the MRO-ai-vision git:

    https://gitlab-int.nlr.nl/spirtovicd/mro-ai-vision, specifically the arbi_detection_deploy.ipynb notebook.


    Also, make sure to not run this model on the training images. This would skew the results. 15 test images were used. 
    The resulting reference sticker detection is shown in Imaging_pipeline_backbone\Defect_detected_final_images.

    Args:
        WorkingDirectory (str): path to the working directory of the pipeline.
        Defect_detection_threshold (float): Threshold for the defect detection model. 
    """

    def __init__(self, WorkingDirectory, Modelpath, Defect_detection_threshold) -> None:

        # Loading & saving parameters
       self.Working_directory = WorkingDirectory
       self.Image_directory = join(WorkingDirectory, "4.Enrichment_images")
       self.image_paths = []
       self.model_path = Modelpath
       self.defect_images_dict = {}

       # tuple which contains all file types which will be loaded
       self.filetypes = ('*.png', '*.jpg', '*.tiff', '*.jpeg', '*.npy')

       # Setup logger
       self.logger = logging.getLogger(__name__)

       # Threshold defect detection
       self.threshold = Defect_detection_threshold

    def load_images(self, collaborator: Acquisition = None):
        """
        This function can be used to load the images before doing the defect detection step.

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

            for files in self.filetypes:
                self.image_paths.extend(glob.glob(join(self.Image_directory, files)))

            if not exists(self.Image_directory):
                self.logger.error(f"Image directory: {self.Image_directory} does not exist!")
                sys.exit(1)

        self.logger.info(f"{__name__} - {len(self.image_paths)} images loaded from {self.Image_directory}") 
        return

    def load_model(self):
        if not exists(self.model_path):
            self.logger.info(f"{__name__} - {self.model_path} does not exist.")
            self.model_path = input("Please enter the path to the defect detection model (.ts file):")

        
        self.model = torch.jit.load(self.model_path, map_location=torch.device('cpu'))

        self.logger.info(f"{__name__} - Defect detection model loaded from {self.model_path}") 
        return

    def defect_detection(self):
        for image_path in self.image_paths:
            img_int = read_image(image_path)

            output_dict = self.model.forward([{'image': img_int}])[0]

            boxes = output_dict['pred_boxes'][output_dict['scores'] > self.threshold]
            colors = output_dict['pred_classes'][output_dict['scores'] > self.threshold].numpy()
            scores = output_dict['scores'][output_dict['scores'] > self.threshold]

            if len(colors) == 0:
                continue

            cols = ['#%06X' % random.randint(0, 0xFFFFFF) for i in range(max(colors)+1)]
            colors = [cols[i] for i in colors]

            result = draw_bounding_boxes(image=img_int, colors=colors, boxes=boxes, width=3)

            # Draw bounding boxes
            defect_detected_img = Image.fromarray(result.permute(1,2,0).numpy())

            # Add the scores in the image
            Draw_img = ImageDraw.Draw(defect_detected_img)
            font = ImageFont.truetype("arial.ttf", 15)

            for i, box in enumerate(boxes):
                    match = re.search("0.[0-9]*", str(scores[i]))
                    score_str = match.group(0) 
                    Draw_img.text(box.detach().numpy()[2:],score_str,fill = "black", font=font)

            self.defect_images_dict[image_path] = defect_detected_img
            
    def save_images(self):
        NewImageDir = join(self.Working_directory, "5.DefectDetected_images")

        if not exists(NewImageDir):
            makedirs(NewImageDir)
        else:
            # This overwrites already existing results
            for filename in listdir(NewImageDir):
                remove(join(NewImageDir, filename))

        for path, image in self.defect_images_dict.items():
            image.save(join(NewImageDir, basename(path)))
        return

    def main(self):
        self.load_images()
        self.load_model()
        self.defect_detection()
        self.save_images()
        return