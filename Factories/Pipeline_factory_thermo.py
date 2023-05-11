"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Concrete factory classes. 

Concrete Factories produce a family of products that belong to a single
family. The factory guarantees that resulting products are compatible. Note
that signatures of the Concrete Factory's methods return an abstract
product, while inside the method a concrete product is instantiated.
Hence, the concrete product must implement the abstract product. In this way, 
the client code can use the methods in the abstract products independent of the conrete products.

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


from ConcreteProducts.Thermography.Acquisition_thermo_PassImages import Acquisition_Thermo
from ConcreteProducts.Thermography.Preprocess_thermo import Preprocess_Thermo
from ConcreteProducts.Thermography.Enrichment_thermo import Enrichment_Thermo
from ConcreteProducts.Thermography.IQA_thermo import IQA_Thermo
from ConcreteProducts.Thermography.DefectDetection_thermo import DefectDetection_Thermo
from Factories.Abstract_factory_and_products import AbstractPipelineFactory, Acquisition, IQA, Preprocess, Enrichment, DefectDetection


class ConcreteFactory_Thermo(AbstractPipelineFactory):
    """
    Thermography pipeline concrete factory class. Each create method returns abstract products 
    but they are implemented by the concrete thermography products. 

    Args:
        Working_directory (str): path to the working directory of the pipeline.
        ParametersPath (str): path to the JSON parameter file
    """
    def __init__(self, WorkingDirectory: str = "", ParameterPath: str = "") -> None:
        super().__init__(WorkingDirectory, ParameterPath, "Thermography Pipeline")
        self.logger.info(f"Creating {self.PipelineName}!")
       
    def create_Acquisition(self) -> Acquisition:
        # This is an example of how parameters can be loaded from the JSON file. 
        # You can specify the module name (e.g. Acquisition) and use a dictionary to index the specific parameters
        # The Acquisition params will be loaded from the JSON file. It is a dictionary with the keys specified in the JSON file.
        # In this case, only the image directory is loaded as a parameter.
        Acquisition_params = next(item for item in self.params_list if item["Module_name"] == "Acquisition")

        if "Image_directory" in Acquisition_params:
            Image_dir = Acquisition_params["Image_directory"]
        else:
            Image_dir = ""

        return Acquisition_Thermo(WorkingDirectory= self.WorkingDirectory, ImageDirectory=Image_dir)

    def create_IQA(self) -> IQA:
        IQA_params = next(item for item in self.params_list if item["Module_name"] == "IQA")
        return IQA_Thermo(WorkingDirectory = self.WorkingDirectory, BrisqueThreshold = IQA_params['Brisque_threshold'])
    
    def create_Preprocessing(self) -> Preprocess:
        Preprocess_params = next(item for item in self.params_list if item["Module_name"] == "Preprocessing")
        return Preprocess_Thermo(WorkingDirectory=self.WorkingDirectory, filter_size=Preprocess_params.get('filter_size'))

    def create_Enrichment(self) -> Enrichment:
        return Enrichment_Thermo(WorkingDirectory=self.WorkingDirectory)
    
    def create_DefectDetection(self) -> DefectDetection:
        defect_detection_params = next(item for item in self.params_list if item["Module_name"] == "DefectDetection")

        if "Modelpath" in defect_detection_params:
            Model_path = defect_detection_params["Modelpath"]
        else:
            Model_path = ""

        return DefectDetection_Thermo(WorkingDirectory=self.WorkingDirectory, Modelpath=Model_path, Defect_detection_threshold=defect_detection_params["defect_detection_thresh"])