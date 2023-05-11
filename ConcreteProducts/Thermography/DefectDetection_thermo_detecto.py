import glob
import sys
from os.path import exists, join, basename
from os import listdir, remove, makedirs
from PIL import Image, ImageDraw, ImageFont, ImageOps
import matplotlib.pyplot as plt
from detecto import core, utils
from detecto.visualize import show_labeled_image
import pandas as pd
import numpy as np
import re

from Pipeline_factories import Acquisition, DefectDetection
import logging

class DefectDetection_Thermo(DefectDetection):
    def __init__(self, WorkingDirectory, Modelpath) -> None:
        # Loading & saving parameters
       self.Working_directory = WorkingDirectory
       # self.Image_directory = r"C:\Users\hoftijzer\Documents\Working_dir\Enrichment_images PCA"
       self.Image_directory = join(WorkingDirectory, "4.Enrichment_images")
       self.image_paths = []
       self.images_dict = {}
       self.model_path = Modelpath

       # tuple which contains all file types which will be loaded
       self.filetypes = ('*.png', '*.jpg', '*.tiff', '*.jpeg', '*.npy')

       # Setup logger
       self.logger = logging.getLogger(__name__)

       # Dataframe containing the all the info from the detected sticker locations
       self.total_df=pd.DataFrame()


    def load_images(self, collaborator: Acquisition = None):
        """
        This function can be used to load the images before doing the enrichment step.

        Args: 
            collaborator (optional): Another concrete product which has a load_images() method which returns the image paths (e.g. the empty acquisition module).
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

        for image_path in self.image_paths:
            if image_path.endswith(".npy"):
                image = np.load(image_path)
            else:
                image = Image.open(image_path)
            
            self.images_dict[image_path] = image

        self.logger.info(f"{__name__} - {len(self.images_dict)} images loaded from {self.Image_directory}") 
        return

    def load_model(self):
        if not exists(self.model_path):
            self.logger.info(f"{__name__} - {self.model_path} does not exist.")
            self.model_path = input("Please enter the path to the defect detection model (.pth):")

        self.model = core.Model.load(self.model_path, ["Marker", "Template"])

        self.logger.info(f"{__name__} - {self.model} loaded from {self.model_path}") 
        return

    def Defect_detection(self):
        """
        This function uses a trained Detecto model in order to detect the GOM stickers in thermography images. It outputs the images with a boundary box and displays the score for each box.
        Also, it outputs a dataframe containing the coordinates of the boundary boxes, scores and center location of each boundary box.
        """
        for path, image in self.images_dict.items():

            # Copy image to make sure to not overwrite image in images_dict
            # Output_img = image.copy()
        
            if path.endswith(".npy"):
                print("skip")
                # image_arr =  image[:,:,0]
                # Pick first dimension to visualize output as grayscale image
                # Output_img = ImageDraw.Draw(Image.fromarray(image[:,:,0]))  #np.ndarray
            else:
                Output_img = image.copy()
                image_arr = utils.read_image(path)
                Draw_img = ImageDraw.Draw(Output_img)


                predictions = self.model.predict(image_arr) #Only works for RGB (3 channels) images.....
                labels, boxes, scores = predictions
                thresh=0.5          #TODO: Put this in parameter file!!
                filtered_indices=np.where(scores>thresh)
                filtered_scores=scores[filtered_indices]
                filtered_boxes=boxes[filtered_indices] #torch.tensor
                num_list = filtered_indices[0].tolist()
                filtered_labels = [labels[i] for i in num_list]    

                font = ImageFont.truetype("arial.ttf", 15)

                for i, box in enumerate(filtered_boxes):
                    match = re.search("0.[0-9]*", str(filtered_scores[i]))
                    score_str = match.group(0) 
                    Draw_img.rectangle(box.numpy(), outline ="black")
                    Draw_img.text(box.numpy()[2:],score_str,fill = "black", font=font)
            
                # show_labeled_image(image, filtered_boxes, filtered_labels)

                xmin = filtered_boxes[:,0].numpy()
                ymin = filtered_boxes[:,1].numpy()
                xmax = filtered_boxes[:,2].numpy()
                ymax = filtered_boxes[:,3].numpy() 
                data = {
                    "filename": path,
                    "image" : Output_img,
                    "x-min": xmin,
                    "y-min": ymin,
                    "x-max": xmax,
                    "y-max": ymax,
                    "Box_y_size": xmax-xmin,
                    "Box_x_size": ymax-ymin,
                    "x":((xmin+xmax)/2),
                    "y":((ymin+ymax)/2)
                }

                df = pd.DataFrame(data)
                self.total_df = self.total_df.append(df) # TODO: Replace with df.concat
                print(self.total_df) #TODO: Remove this

            # LOG statement

        self.total_df.to_pickle(r"C:\Users\hoftijzer\Documents\Working_dir\normal_dataframe.pkl") #TODO: Make method of this to store data
        return


    def save_images(self):
        NewImageDir = join(self.Working_directory, "5.DefectDetected_images")

        if not exists(NewImageDir):
            makedirs(NewImageDir)
        else:
            # This overwrites already existing results
            for filename in listdir(NewImageDir):
                remove(join(NewImageDir, filename))
        
        total_df_wo_duplicates = self.total_df.copy().drop_duplicates(subset='filename')

        for index, row in total_df_wo_duplicates.iterrows():
            row['image'].save(join(NewImageDir, basename(row['filename'])))
        return

    def main(self):
        self.load_images()
        self.load_model()
        self.Defect_detection()
        self.save_images()
        return