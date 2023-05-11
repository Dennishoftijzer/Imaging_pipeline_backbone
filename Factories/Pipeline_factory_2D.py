"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Concrete factory classes. 

Concrete Factories produce a family of products that belong to a single
family. The factory guarantees that resulting products are compatible. Note
that signatures of the Concrete Factory's methods return an abstract
product, while inside the method a concrete product is instantiated.
Hence, the concrete product must implement the abstract product. In this way, 
the client code can use the methods in the abstract products independent of the conrete products.

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


from ConcreteProducts.Empty_products_2D import *
from Factories.Abstract_factory_and_products import AbstractPipelineFactory, Acquisition, IQA, Preprocess, Enrichment, DefectDetection

class ConcreteFactory_2D(AbstractPipelineFactory):
    """
    2D pipeline concrete factory class. Each create method returns abstract products 
    but they are implemented by the concrete 2D products.

    Args:
        Working_directory (str): path to the working directory of the pipeline.
        ParametersPath (str): path to the JSON parameter file 
    """
    def __init__(self, WorkingDirectory: str = "", ParameterPath: str = "") -> None:
        super().__init__(WorkingDirectory, ParameterPath, "2D Pipeline")
        self.logger.info(f"Creating {self.PipelineName}!")

    def create_Acquisition(self) -> Acquisition:
        return Acquisition_2D()

    def create_IQA(self) -> IQA:
        return IQA_2D()
    
    def create_Preprocessing(self) -> Preprocess:
        return Preprocess_2D()

    def create_Enrichment(self) -> Enrichment:
        return Enrichment_2D()
    
    def create_DefectDetection(self) -> DefectDetection:
        return DefectDetection_2D()