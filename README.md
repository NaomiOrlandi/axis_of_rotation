# Axis of Rotation

## **Introduction**
### **Tomographic system**

Nowadays the most used non- invasive imaging techniques in cultural heritage field are x-ray tomography and neutron tomography.

Computed tomography is a method to acquire three dimensional information about the structure inside a sample.
The following figure shows a typical neutron tomography setup. where the neutron beam interact with the rotating sample, so the attenuated neutrons are converted into visible light by a scintillator, that is collected by a CCD camera.

![tomo system](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/documentation_images/imaging_system.PNG "tomo system")

The neutron beam interacts with the sample. The attenuated neutrons are converted into visible light by a scintillator. Finally light is collected by a CCD camera and a radiographic image is acquired.
The sample is rotating, hence radiographic projection images are acquired from many views to reconstruct the distribution of materials in the sample. Mostly, the projections are acquired with equiangular steps over either 180° or 360° to cover the whole sample.
A component of the sample is highly visible in the radiography if strong attenuation occurs during the interaction between the beam particles and that component.  
X-ray and neutron tomographic images show different features also because of their interactions with matter.  
In fact, X-rays, that are strongly attenuated by high atomic number elements, like metals, are excellent in the analysis of biological materials.
Neutrons, instead, are quite sensitive to light atoms like hydrogen, oxygen, etc. and interact with low probability with metals, allowing a high penetration depth.

### **Tomographic reconstruction**
The radiographic projection data are usually transformed into a three dimensional image of the sample by computationally intensive reconstruction algorithms.
The result of the algorithms is affected by the quality of the acquired images and by the knowledge of the axis of rotation of the sample with respect to the detector.

The image quality can be improved during a preprocessing stage.  
Regarding the axis of rotation, some detection methods can be applied directly to measured projection data, saving valuable measurement time.

#### **Preprocessing**
Some of the improvment of of the images are cropping, normalization and the outliers filtering.

 - **Cropping.**  
   It's the removal of unwanted outer areas of an image, selecting just the region where a relevant signal is collected and the sample is visible.

- **Normalization.**  
   It is a process that changes the range of pixel intensity values. Also called contrast stretching, it enhances the contrast of the image.
   Each normalized px intensity is calculated with the following formula,  

   ![I](https://latex.codecogs.com/svg.image?-ln(%5Cfrac%7BI-I_%7Bmin%7D%7D%7BI_%7Bmax%7D-I_%7Bmin%7D%7D))

   where *I<sub>new</sub>* is the new px intensity, *I* is the old px intensity, *I<sub>min</sub>* is the px intensity of the dark image, *I<sub>max</sub>* is the px intensity of the flat image acquired with light on and without the sample and ln is the natural logarithm.

- **Outliers filtering.**  
   It is a nonlinear process that reduces random or salt-and-pepper noise and preserves edges in an image. It's useful for correcting, e.g., hot pixels or dead pixels of a CCD image.  
   A promising method is to perform the weighted combination of images. It better improves the SNR of images and reduces the number of outliers with respect to simply compute the average or the median of images[[1]](#1).  

   ![fcorr](https://latex.codecogs.com/svg.image?f_%7Bcorrected%7D(x,y)%20=%20%5Csum_%7Bi=1%7D%5E%7BN%7D%7Bw_i(x,y)%20%5Ccdot%20f_i(x,y)%7D)

   where *f<sub>corrected</sub>(x,y)* is the corrected image, *f<sub>i</sub>(x,y)* is one of the images that will be combined, *w<sub>i</sub>(x,y)* is the corresponding weight.  
   One possibility is to use the original image and its median as combining images and to set *w<sub>i</sub>(x,y)* as 0 or 1 if the original px value differs from the median by a certain threshold or not. Hence:

   ![fcorr1](https://latex.codecogs.com/svg.image?f_%7Bcorrected%7D(x,y)%20=%20w(x,y)%5Ccdot%20f_%7Boriginal%7D(x,y)%20&plus;%20(1-w(x,y))%5Ccdot%20f_%7Bmedian%7D(x,y))


#### **Determining rotation axis position**

![COR](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/documentation_images/tilted_system.PNG "COR")

The figure shows a standard tomography acquisition system and one with a certain tilt angle of the sample axis of rotation.
Sometimes the latter can be even horizontally shifted.

The current main methods of determining the centre of rotation (*COR*) are center-of-sinogram method, geometrical method, the opposite-angle method, and iterative method [[2]](#2). For what regards the opposite_angle method, maximum cross correlation or minimum squared error between two opposite projection can be considered.

Assuming to use the second technique and that the two opposite projections are the one acquired at 0° and the one acquired at 180°, then the *COR* is estimated with the following formula[[3]](#3):

![COR](https://latex.codecogs.com/svg.image?COR%20=%20min_x%20%5Csum_%7Bi=1%7D%5EN(p_0(x&plus;i)-p_%7B180%7D(N-i))%5E2)

where *COR* is the centre of rotation, *p<sub>0</sub>* represents the projection image at 0°, *p<sub>180</sub>* stands for the projection at 180° and *x* is the horizontal px position in the image.
The calculation is repeated for all the vertical positions.  
Once all the horizontal shift are calculated, a polynomial fit is performed between them and the vertical coordinates, in order to estimate the tilted angle and the offset of the sample axis of rotation with respect to the central vertical axis of the images, i.e., determine the position of the *COR* precisely.

## **Project**

This project has the aim of determining the position of the sample axis of rotation with respect to the central axis of the detector, that is the central vertical axis of the images, given a stack of tomographic projection images. The latters can be corrected and new images will have the rotation axis coincident with the central vertical axis of the images.
The user has also the possibility to perform preprocessing on the images (one or more of the following operations):

- cropping
- normalization
- outliers filtering


The projection images must be of .tiff format and the tomography has to be performed with a maximum angle of 180° or 360°.
A flat and a dark image or stack of the same format are required.

## **Installation**
Clone the repository [axis_of_rotation](https://github.com/NaomiOrlandi/axis_of_rotation), then create a conda environment with the dependencies expressed in *environment.yml*, activate it and use the package manager [pip](https://pip.pypa.io/en/stable/) to install the application.

```
git clone https://github.com/NaomiOrlandi/axis_of_rotation
cd axis_of_rotation
conda env create -f environment.yml
conda activate axrot
pip install COR
```

## **Usage**

When COR is installed, the user has to modify the *configuration.ini* file or write another configuration file with the extension .ini and with the same structure of *configuration.ini* file. Then he/she can simply type on command line `python COR config_file.ini <optional arguments>`.  
where `config_file.ini` is the configuration file chosen by the user.
In order to have a description of the positional and optional arguments, type `python COR -h` or `python COR --help`
### **Positional argument**
- `config_file` : the path of the configuration file;
### **Optional arguments**
- `-roi` : it allows to perform the cropping of all the tomographic projection images, drawing a ROI on one of them;

- `-norm` : images in the stack are normalized, considering flat and dark images. If the images were cropped, the result will be a stack of images with crop dimensions;

- `-outliers` : images are filtered from bright, dark or both outliers.

Once preprocessing is performed, the position estimate of the sample axis of rotation (offset and tilt angle) is computed.
Then the user, looking at the figures that represent the results, can decide whether to correct the images, to perform again the estimate or to exit and abort the script.

ROI coordinates (if images are cropped) and rotation axis position will be saved in file *data.txt*, while the corrected images in a path specified in the configuration file.

## **Structure**
The program in structured as the following:

1. a [configuration file](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/configuration.ini) in which the user has to specify the path of the folders containing the .tiff projection images, the flat image or images and the dark image or images in section **[directories]**.  
Note: the number of flat and dark images must be 1 or the same of the number of tomographic projections.
In section **[angle]** the user specifies the last acquisition angle.
In **[outlier filter]**, if the user wants to perform an outliers filtering, the number of neighborhood pixels has to be specified.  
Finally in section **[final files]** are stored the desired path for a file *data.txt* in which will be written the offset and the tilt angle of the rotation axis and the coordinates of the region of interest (ROI) if cropping is performed, the path of the folder that will contain the corrected projections with the prefix of the name of the new files, and the number of digits of the numbering for the new files.

2. a [file for the preparation of data](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/COR/preparation_data.py), where there are the following functions:  

   - **reader_grey_images**, that reads grey scaled images contained in a specified filepath;
   - **create_array**, that converts a list of images to a 3D array;
   - **projection_0_180**, that selects the projections at 0° and 180° from a stack of projections.

3. a [file for the preprocessing and the correction of the images](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/COR/preprocess_and_correction.py) and [one for the interactions of the user with the program](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/COR/user_interaction.py), where the functions for the correction of the images and for their eventual preprocessing are collected.

   For the preprocessing:  

   **Cropping**
   - **draw_ROI**, which allows to select interactively a rectangular a region of interest (ROI) on an image;
   - **save_ROI**, which saves the coordinates of the ROI in the file *data.txt*;
   - **cropping**, which crops all the images of the stack considering the coordinates of a ROI.

   **Normalization**
   - **normalization**, that normalizes all the images in the stack considering flat and dark images.

   **Outliers filter**
   - **outliers_filter**, which removes bright or dark or both outliers from a stack of images, through the method described in [Preprocessing](#Preprocessing). The threshold is global and is set to 0.02.  

   For the images correction:

   **Estimate of centre of rotation**
   - **ROIs_for_correction**, that allows to select one or multiple ROIs in the projections that will be considered when searching for the axis of rotation offset and tilt angle in the following function;
   - **find_shift_and_tilted_angle**, that estimates the offset and the tilt angle of the rotation axis with respect to the detector using the projections at 0° and at 180°, computing the method described in [Preprocessing](#Preprocessing);
   - **graph_axis_rotation**, which shows two figures that report the results of *find_shift_and_tilt_angle* function.

   **Images correction**
   - **correction_axis_rotation**, that performs the correction of all the images in the stack, according to the shift and tilt angle of the axis of rotation with respect to the central vertical axis of the images and save the results in *data.txt*
   - **save_images**, which saves the new images in the folder path specified by the user in the congifuration file and with the desired name and numbering.

4. a [file for the visualization of the stack of projection images](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/COR/show_stack.py), allowing to scroll through the images.

5. a [file main](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/COR/main.py), which let the user visualize the images of the stack, then it includes all the possible combinations for preprocessing and the correction of the images in all cases.

6. a last [file for the correction of the filename](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/possible%20utils/change_filename.py) of the available images has been put in the folder *possible utils*. It can be used to change the numbering of the image files, adding zeros on the left, when necessary.

   Example: {image_1, image_2, ..., image_15} -> {image_01, image_02, ..., image_15}

7. two testing files, one for the [part of preparation of data](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/test_preparation_data.py) and one for the [part of preprocessing and the correction of images](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/test_preprocess_and_correction.py).
In both the files, property and unit tests are present. A folder called *testing_images* contains the image files used to perfom some tests.

For a more detailed description of the functions, see the [documentation for functions](https://github.com/NaomiOrlandi/axis_of_rotation/tree/main/documentation_functions).



## **Example**
The folder [example_dataset](https://github.com/NaomiOrlandi/axis_of_rotation/tree/main/example_dataset) contains an example of data structure, usable with the application.   
In [projections](https://github.com/NaomiOrlandi/axis_of_rotation/tree/main/example_dataset/projections) 181 x-ray tomoographic projection images of a wooden cube with two holes are stored. The last angle of acquisition is 360°. The tilt angle of the sample rotation axis is known and it is 2°. 
In [flat](https://github.com/NaomiOrlandi/axis_of_rotation/tree/main/example_dataset/flat) and [dark](https://github.com/NaomiOrlandi/axis_of_rotation/tree/main/example_dataset/dark) are contained rispectively the flat and dark images of the same acquisition.

In this example *configuration.ini* is considered as configuration file and the user inserts the correct filepaths for the initial images, for the corrected ones and for *data.txt*, the variable *angle* as 360 and *radius_neighborhood* that can be any desired integer for the outliers filtering (in this example it is 5).

### **Example with cropping, normalization and bright and dark outliers filtering**

Once the configuration file is prepared, open the command line and type 

`python COR configuration.ini -roi -norm -outliers`

The passages will be the following:

1. All the grey scaled images are read and the stack of projections is visualized with the possibility to scroll through the images.

   <img src="https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/documentation_images/visualization_proj.PNG" width="50%" height="50%">

2. The first image of the stack is shown to allow the user to select manually the region of interest (ROI), that will be used for cropping all the stack projections.

   <img src = "https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/documentation_images/select_ROI.PNG" width = "50%" height = "50%">

3. The normalization is performed considering the projection images, the coordinates of the cropping ROI and dark and flat images.

4. The user is asked to choose which kind of outliers to remove from the images. In this example the filtering is performed for dark and bright outliers:

   ```
   > Do you want to perform a filtering from bright outliers,dark outliers or both?     
   [B] filter just bright outliers
   [D] filter just dark outliers
   [A] filter both bright and dark outliers
   Type your answer and press [Enter] :a
   ```
5. ```
   To compute the rotation axis position it is necessary to select one or multiple regions where the sample is present.
   Hence you must draw the different regions vertically starting from top to bottom.
   > Insert the number of regions to select:
   ```
   In this example 1 region is selected (where the sample is visible and without background above and below it, in order to avoid noise in the region):

   <img src = "https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/documentation_images/ROI_for_corr.PNG" width = "50%" height = "50%">

   After the computation of the position of the rotation axis of the sample, the command line will show the following:

   ```
   Rotation axis Found!
   offset = 24.5    tilt angle = -2.0192550867664587 °
   average of residuals  =  0.01322056
   ```

   And the following images are visualized:

   ![before](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/documentation_images/before_corr.PNG "before")

   ![after](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/documentation_images/after_corr.PNG "after")

6. ```
   > Rotation axis found. Do you want to correct all projections?
   [Y] Yes, correct them.
   [N] No, find it again.
   [C] Cancel and abort the script.
   Type your answer and press [Enter] :
   ```

   For the images correction, type `y` or `Y`.

   The corrected stack of projection is shown and saved in the path specified in *configuration.ini*

   The created file *data.txt*, whose location is written in the configuration file, contains the coordinates of the cropping ROI, the offset and the tilt angle of the sample rotation axis:
   ```txt
   rowmin 28 
   rowmax 958 
   colmin 55 
   colmax 1072
   shift 36 
   tilt angle -2.0187374650361463
   ```
   Point (0,0) is at the top left of the image.

## **Test routine**

   Tests for file *prepatation_data.py* are in *test_preparation_data.py* and tests for *preprocess_and_correction.py* are in *test_preprocess_and_correction.py*.
   Invoke the pytest module to perform all the tests.

   ```
   pytest
   ========================================== test session starts ===========================================
   platform win32 -- Python 3.8.10, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
   rootdir: C:\Users\Naomi\correctionCOR
   plugins: hypothesis-6.34.1
   collected 31 items

   test_preparation_data.py ...........                                                                [ 33%]
   test_preprocess_and_correction.py ....................                                               [100%]

   ===================================== 31 passed in 44.13s  ====================================== 
   ```


## **References**
<a id="1">[1]</a> Anders. P. Kaestner, *Methods to Combine Multiple Images to Improve Quality*, Materials Research Proceedings, Vol. 15, pp 193-197, 2020
https://doi.org/10.21741/9781644900574-30

<a id="2">[2]</a> Yang Min, Gao Haidong, Li Xingdong, Meng Fanyong, Wei Dongbo,
*A new method to determine the center of rotation shift in 2D-CT scanning system using image cross correlation*,
NDT & E International,
Vol. 46,
2012,
pp 48-54,
ISSN 0963-8695,
Introduction,
https://doi.org/10.1016/j.ndteint.2011.09.001.

<a id="3">[3]</a> Anders P. Kaestner,
*MuhRec—A new tomography reconstructor*,
Nuclear Instruments and Methods in Physics Research Section A: Accelerators, Spectrometers, Detectors and Associated Equipment,
Vol. 651, Issue 1,
2011,
pp 156-160,
ISSN 0168-9002,
https://doi.org/10.1016/j.nima.2011.01.129.


