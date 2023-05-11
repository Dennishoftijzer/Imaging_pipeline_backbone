# Description
This repository contains the backbone for an image processing pipeline to detect defects in aircraft components. The goal was to create a modular imaging pipeline which can work independently of several measurement methods.
Currently, the measurement method can either be 2D acquisition, 3D acquisition or thermography. The pipeline consists of the following modules or steps, 1) Acquisition 2) Image Quality Assessment (IQA) 3) Preprocessing 4) Enrichment 5) Defect detection. Each measurement method (pipeline variant) executes these specific modules but the implementation of the module can differ greatly between the variants, which is shown in the following image: 

![This is an image](README_image/Abstract_factory_matrix.png)

## Abstract factory
To make sure that the pipeline will work independently of the chosen measurement method (pipeline variant), a creational design pattern was used, called abstract factory. For a detailed explanation, see the [Refacturing Guru website](https://refactoring.guru/design-patterns/abstract-factory). In short, a client code will only make use of abstract products (modules such as acquistition) classes. These abstract classes define methods but do not implement them. Instead, they are implemented by concrete products (e.g. 2D acquisition). The actual implementation of these methods can vary greatly between the different concrete products (2D, 3D, thermography) but this is invisible to the client code. Hence, the client code can run no matter of the actual pipeline variant being used! There is one more important notion to the abstract factory. Initilization of concrete products is moved to concrete factory classes, in order to make sure you always obtain concrete products from the same variant (2D, 3D, thermography). To guarantee the client code can still work independently of the pipeline variant, concrete factory classes implement an abstract factory class. Exactly like in the case of the concrete- and abstract product classes, the actual creation methods can vary greatly between the concrete factories but they all implement the methods defined in the abstract factory!

## Thermography pipeline
The following section provides a quick overview of the thermography pipeline. Note that only the thermography pipeline variant has actually been implemented. This pipeline was designed to detect reference point markers in thermography grayscale images. The dataset used contained three grayscale images per inspected part, corresponding to three different excitation frequencies of the lamps. The grayscale values in the images correspond to the temperature phase delay between excitation and the surface. You can find examples [`here`](Example_images).

### Acquisition
Currently, the acquisition module only copies grayscale images from a specified folder to the working directory. The images should follow a certain naming convention and three grayscale images per part should be available. For example: `Flap Lower 0_1Hz 01.png`, `Flap Lower 0_2Hz 01.png` and `Flap Lower 0_5Hz 01.png`. In a later stage, this module could contain acquisition and initialization code for an IR camera as well as excitation control for lamps.

### Image Quality Assessment (IQA)
The IQA module assesses the image quality using the BRISQUE model based on this [`paper`](https://ieeexplore.ieee.org/document/6272356). BRISQUE is a no-reference based method which uses image pixel intensity distributions in order to determine wether an image contains artifacts such as noise or blur. As image quality is a subjective matter, the actual BRISQUE score is the output of a Support Vector Machine (SVM) trained on human evalution of the quality of images. Lower score is better quality, hence only images below a certain threshold will continue in the pipeline.

### Preprocessing
Thermography preprocessing consists of three steps:
1. Slight blur in order to remove dead pixels
2. Outlier removal
3. Contrast & brightness equalization

### Enrichment
The enrichment step will layer the three corresponding (same camera location but different excitation frequencies) grayscale images into one RGB image. Each grayscale image will occupy the red, green or blue channel in order to form the composite image.

### Defect detection
#### Object detection model
The thermography defect detection module uses the [detectron2](https://github.com/facebookresearch/detectron2) library and a pre-trained [faster RCNN](https://github.com/facebookresearch/detectron2/blob/main/configs/COCO-Detection/faster_rcnn_R_50_FPN_1x.yaml) object detection model. 

#### Dataset
The RGB images produced by the enrichment module were split into training- and test images (90-10%) using [roboflow](https://app.roboflow.com/login).

Furthermore, a [mosaic augmententation](https://blog.roboflow.com/advanced-augmentations/) method was applied to the training images before training, combining four randomly cropped images into one training image. This can help with combining the different parts (flap, radome, pipistrel) into one training image.

#### Model inference & deployment
To use the model without detectron2 package dependency, the model was exported using [`torchscript`](https://pytorch.org/tutorials/beginner/Intro_to_TorchScript_tutorial.html) See the [detectron2 documentation](https://detectron2.readthedocs.io/en/latest/tutorials/deployment.html) for more details.
 
The output of the model deployment is in the [`exported_model`](ConcreteProducts/Thermography/Defect_detection_model/exported_model) folder for torchscripting format. Due to the exportation to torchscript, the [`model.ts`](ConcreteProducts/Thermography/Defect_detection_model/exported_model/model.ts) file can now be loaded in the defect detection module and inference is possible without detectron2 package dependencies.


# Installation
1. You can create a new [`Conda`](https://docs.conda.io/projects/conda/en/latest/) environment from the [`environment.yml`](environment.yml):

        conda env create --file ./environment.yml --name pipeline_env 

2. Unfortunatly, the [`BRISQUE package`](https://github.com/bukalapak/pybrisque) used for the thermography IQA contains some improper imports, which you will need to fix manually:
    - Go to your Anaconda3 install directory and locate `brisque.py`. For windows it might look like this:

        `C:\Users\[YOUR_NAME]\.conda\envs\pipeline_env\Lib\site-packages\brisque\brisque.py`

    - Change the following on line 8 & 9:
        ```python
        import svmutil
        from svmutil import gen_svm_nodearray
        ```
        to: 
        ```python
        from libsvm import svmutil
        from libsvm.svmutil import gen_svm_nodearray
        ```

5. Activate the conda environment `pipeline_env` by running:

        conda activate pipeline_env
6. Done! 🤗 

# Usage
- Run [`Client_code.py`](Client_code.py).
    - The `client_code` method has an abstract factory argument. You can pass it one of the concrete factories classes: `ConcreteFactory_Thermo`, `ConcreteFactory_2D` or `ConcreteFactory_3D`.
    - In [`Client_code.py`](Client_code.py) you can optionally specify the working directory and path to the parameter JSON file. In between each module, images are saved to the [`Working directory`](Working_directory).
    - It is recommended to comment out the `sys.settrace(trace)` and `sys.settrace(None)` in [`Client_code.py`](Client_code.py) when using the VS code debugger.
- The [`Factories`](Factories) folder contains all the concrete factory classes (2D, 3D, thermography) in their respective files. All abstract classes are located in ['Abstract_factory_and_products.py'](Factories/Abstract_factory_and_products.py)
- 2D and 3D concrete products are not implemented and located in [`Empty_products_2D.py`](ConcreteProducts/Empty_products_2D.py) and [`Empty_products_3D.py`](ConcreteProducts/Empty_products_3D.py) respectively. The ['Thermography subfolder'](ConcreteProducts/Thermography) contains all thermography concrete products as well as the defect detection detectron2 model.
- You can find the output in the [`5.DefectDetected_images`](Working_directory/5.DefectDetected_images) folder.

## Parameters
Parameters for the entire pipeline are loaded via a JSON file when instantiating a factory object. An example file is shown in [`Example_parameter_file_thermography.JSON`](Example_parameter_file_thermography.JSON) for the thermography pipeline.

## Logging
A log of all methods that are executed, is automatically generated.
To disable logging, comment out `sys.settrace(trace)` and `sys.settrace(None)` in [`Client_code.py`](Client_code.py). The log is stored in `Pipeline_process.log` and prints to the terminal. See e.g. [`ConcreteProducts/Empty_products_2D.py`](ConcreteProducts/Empty_products_2D.py) to learn how you can add the logger to your own products.


