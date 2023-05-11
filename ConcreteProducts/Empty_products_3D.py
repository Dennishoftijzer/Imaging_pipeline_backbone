"""
This file contains concrete products for the 3D pipeline. These have not been implemented yet.
Concrete Products are created by corresponding Concrete Factories (ConcreteFactory_3D in Pipeline_factories.py).
Make sure that the concrete products implement the methods from the abstract products. It also showcases how you can use the logger.
"""
import logging

# These are the abstract products. Concrete products inherit abstract product classes and should implement their abstract methods.
from Factories.Abstract_factory_and_products import Acquisition, IQA, Preprocess, Enrichment, DefectDetection


class Acquisition_3D(Acquisition):
    def __init__(self) -> None:
        # Setup logger
        self.logger = logging.getLogger(__name__)

    def load_images(self) -> list():
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return 

    def save_images(self):
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return 

    def main(self):
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

class IQA_3D(IQA):
    def __init__(self) -> None:
        # Setup logger
        self.logger = logging.getLogger(__name__)

    def load_images(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def Asses(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def save_images(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def main(self):
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return


    # This shows how concrete products can collaborate with each other.
    # Note that products of e.g. the 3D pipeline can only work together with
    # products from the 3D pipeline, although this function accepts an instance
    # of an abstract product. This is done to make sure the client can call this function 
    # independently of which pipeline is used!

    # def another_useful_function_b(self, collaborator: Acquisition) -> str:
    #    result = collaborator.useful_function_a()
    #    return f"The result of the B1 collaborating with the ({result})"

class Preprocess_3D(Preprocess):
    def __init__(self) -> None:
        # Setup logger
        self.logger = logging.getLogger(__name__)

    def load_images(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def Preprocess_steps(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def save_images(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def main(self):
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

class Enrichment_3D(Enrichment):
    def __init__(self) -> None:
        # Setup logger
        self.logger = logging.getLogger(__name__)

    def load_images(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def enrich(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def save_images(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def main(self):
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

class DefectDetection_3D(DefectDetection):
    def __init__(self) -> None:
        # Setup logger
        self.logger = logging.getLogger(__name__)

    def load_images(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def load_model(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def defect_detection(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def save_images(self) -> None:
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return

    def main(self):
        self.logger.info(f"{__name__} - Not implemented yet!") 
        return