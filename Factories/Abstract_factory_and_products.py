from __future__ import annotations
from abc import ABC, abstractmethod
from json import load
from os.path import exists
from os import makedirs
import logging

class AbstractPipelineFactory(ABC):
    """
    The Abstract Factory interface declares a set of methods that return
    different abstract products (Acquisition, IQA, preprocessing, enrichment or defectdetection).
    A family of products may have several variants (3D, 2D or Thermography), but the products of one variant are incompatible with products of
    another e.g. you can't combine 3D acquisition with 2D IQA.

     Args:
            Working_directory (str): path to the working directory of the pipeline.
            ParametersPath (str): path to the JSON parameter file
    """
    def __init__(self, WorkingDirectory: str = "", ParameterPath: str = "", PipelineName: str = "") -> None:
        # Get the logger object to ensure same format
        self.logger = logging.getLogger(__name__)

        # General parameters
        self.PipelineName = PipelineName
        self.WorkingDirectory = WorkingDirectory
        self.ParameterPath = ParameterPath
        self.params_list = []

        # Load parameters from JSON file
        if not exists(self.ParameterPath):
            self.ParameterPath = input("Please enter the path to the parameter JSON file:")

        with open(self.ParameterPath, "r") as jsonFile:
            self.params_list = load(jsonFile)

        self.logger.info(f"{__name__} - ParameterPath: {self.ParameterPath}")

        # Create working directory
        if self.WorkingDirectory == "":
            self.WorkingDirectory = input("Please enter the path to the working directory:")

        self.logger.info(f"{__name__} - WorkingDirectory: {self.WorkingDirectory}")

        if not exists(self.WorkingDirectory):
            makedirs(self.WorkingDirectory)

    # These are abstract factory creation methods which return abstract products. 
    # They are declared in the abstract factory class and later implemented by the concrete factory classes (2D, 3D, Thermography).        
    @abstractmethod
    def create_Acquisition(self) -> Acquisition:
        pass

    @abstractmethod
    def create_IQA(self) -> IQA:
        pass

    @abstractmethod
    def create_Preprocessing(self) -> Preprocess:
        pass

    @abstractmethod
    def create_Enrichment(self) -> Enrichment:
        pass

    @abstractmethod
    def create_DefectDetection(self) -> DefectDetection:
        pass


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Abstract products.

Abstract products declare an interface for related products (Acquisition, IQA, etc.) in the different families.
All family variants (2D, 3D, Thermohraphy) of the product must implement this interface.

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class Acquisition(ABC):
    """
    Abstract product for the Acquisition module. All concrete acquisition product variants (2D, 3D, thermography)
    inherit this class. Concrete acquisition products should implement the abstract methods in this class.
    """
    @abstractmethod
    def load_images(self) -> None:
        pass

    @abstractmethod
    def save_images(self) -> None:
        pass

    @abstractmethod
    def main(self) -> None:
        pass

class IQA(ABC):
    """
    Abstract product for Image Quality Assessment (IQA) module. All concrete IQA product variants (2D, 3D, thermography)
    inherit this class. Concrete IQA products should implement the abstract methods in this class.
    """
    @abstractmethod
    def load_images(self) -> None:
        pass

    @abstractmethod
    def Asses(self) -> None:
        pass

    @abstractmethod
    def save_images(self) -> None:
        pass

    @abstractmethod
    def main(self) -> None:
        pass

    
class Preprocess(ABC):
    """
    Abstract product for preprocessing module. All concrete Preprocess product variants (2D, 3D, thermography)
    inherit this class. Concrete preprocess products should implement the abstract methods in this class.
    """
    @abstractmethod
    def load_images(self, collaborator):
        pass

    @abstractmethod
    def Preprocess_steps(self):
        pass

    @abstractmethod
    def save_images(self):
        pass

    @abstractmethod
    def main(self) -> None:
        pass

class Enrichment(ABC):
    """
    Abstract product for enrichment module. All concrete Enrichment product variants (2D, 3D, thermography)
    inherit this class. Concrete Enrichment products should implement the abstract methods in this class.
    """
    @abstractmethod
    def load_images(self, collaborator):
        pass

    @abstractmethod
    def enrich(self) -> None:
        pass

    @abstractmethod
    def save_images(self):
        pass

    @abstractmethod
    def main(self) -> None:
        pass

class DefectDetection(ABC):
    """
    Abstract product for defect detection module. All concrete defect detection product variants (2D, 3D, thermography)
    inherit this class. Concrete defect detection products should implement the abstract methods in this class.
    """
    @abstractmethod
    def load_images(self, collaborator):
        pass

    @abstractmethod
    def load_model(self) -> None:
        pass

    @abstractmethod
    def defect_detection(self) -> None:
        pass

    @abstractmethod
    def save_images(self) -> None:
        pass

    @abstractmethod
    def main(self) -> None:
        pass