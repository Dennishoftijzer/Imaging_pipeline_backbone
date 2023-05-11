import os
import re

from Factories.Abstract_factory_and_products import AbstractPipelineFactory
from Factories.Pipeline_factory_2D import ConcreteFactory_2D
from Factories.Pipeline_factory_3D import ConcreteFactory_3D
from Factories.Pipeline_factory_thermo import ConcreteFactory_Thermo

import logging
import sys

from os.path import join, basename

def setup_logger():
    """
    This function sets up the root logger in order to log the process of the pipeline. The logging level is set to info, meaning INFO, WARNING, ERROR and CRITICAL levels will be logged.
    The logger will print to the terminal and write to the Pipeline_process.log file. It already logs any method executed by the factories or products using the trace function below.
    To add the logger to a concrete product class, import logging and add the following to the __init__ method:

    self.logger = logging.getLogger(__name__)

    You can use self.logger.info(f"{__name__} - <message>") to log any relevant info.
    """
    # Create handlers for terminal and writing to file
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('Pipeline_process.log', mode='w')

    # Create formatters and add it to handlers
    format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S") #%(name)s
    c_handler.setFormatter(format)
    f_handler.setFormatter(format)

    logging.basicConfig(level=logging.INFO, handlers=[c_handler, f_handler])

    return 

def trace(frame, event, arg):
    """
    This function registers the traceback (info that is returned when an event happens in the code) to the python interpreter and logs it using the logger.
    This is done to log all the methods performed in the concrete products. It logs all methods performed in the pipeline directory and Concreteproducts subdir.
    """
    # List all files in the pipeline directory for logger
    filename_ls = os.listdir(os.path.dirname(__file__))

    # Add the files in concrete products subdir
    filename_ls.extend(os.listdir(join(os.path.dirname(__file__), "Concreteproducts")))
    filename_ls.extend(os.listdir(join(os.path.dirname(__file__), "Concreteproducts/Thermography")))
    filename_ls.extend(os.listdir(join(os.path.dirname(__file__), "Factories")))

    # Remove __init__.py and __pycache__ from list
    regex = re.compile('__[a-z]*__')
    filename_ls = [s for s in filename_ls if not regex.search(s)]
    
    # To prevent the logger from logging generator expressions 
    functions_no_log_ls = ["<genexpr>", "<listcomp>"]

    if event == "call":
        # extracts code object executed by current frame
        code = frame.f_code
        
        filename = basename(code.co_filename)
        if filename in filename_ls:
            lineno = frame.f_lineno

            # extracts calling function name
            func_name = code.co_name

            # Log info
            if not func_name in functions_no_log_ls:
                logger.info(f"{filename} - {func_name} - line {lineno}")
    return trace

def client_code(factory: AbstractPipelineFactory) -> None:
    """
    Refactoring guru gives a detailed explanation of the abstract factory pattern:

    https://refactoring.guru/design-patterns/abstract-factory


    The client code works with factories and products only through abstract
    types: AbstractPipelineFactory and Abstract products (Acquistion, IQA, preprocess, ...). This lets you pass any factory
    or product subclass to the client code without breaking it.
    """
    product_a = factory.create_Acquisition()
    product_a.main()

    product_b = factory.create_IQA()
    product_b.main()
 
    product_c = factory.create_Preprocessing()
    product_c.main()

    product_d = factory.create_Enrichment()
    product_d.main()

    product_e = factory.create_DefectDetection()
    product_e.main()

if __name__ == "__main__":
    """
    The client code can work with any concrete factory class.
    """
    # Create logger
    setup_logger()
    logger = logging.getLogger(__name__)

    # Register traceback (info that is returned when an event happens in the code) to python interpreter
    # It is recommended to comment this out when using the debugger!
    # sys.settrace(trace)

    # The working directory is where all images will be stored in between each module
    Working_directory = r"./Working_directory"

    # Parameters for all modules are loaded via a JSON file
    ParameterPath = r"Example_parameter_file_thermography.JSON"

    client_code(ConcreteFactory_Thermo(WorkingDirectory=Working_directory, ParameterPath=ParameterPath))

    # You can choose a different pipeline by giving an instance of another factory to the client code:
    # client_code(ConcreteFactory_3D(ParameterPath=ParameterPath))

    # Also comment this when using debugger!
    sys.settrace(None)

