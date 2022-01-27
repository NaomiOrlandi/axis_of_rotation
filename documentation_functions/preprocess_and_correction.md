# **Preprocess_and_correction.py**
This library contains all the functions for the preprocessing of projection images and that ones for the determination of the sample axis of rotation with respect to the detector and the correction of the images. 
[Source of the file](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/COR/preprocess_and_correction.py)

## **Preprocessing**

## `save_ROI (rowmin,rowmax,colmin,colmax,datapath)`

This function creates or open a file called *data.txt* in the path datapath and save the coordinates of the ROI.

**Parameters:**  
- **rowmin : int**  
The minimum row coordinate.

- **rowmax : int**  
The maximum row coordinate.

- **colmin : int**  
The minimum column coordinate.

- **colmax : int**  
The maximum column coordinate.

- **datapath : str**  
string representing the directory path where to create *data.txt* 

## `cropping (img_stack,rowmin,rowmax,colmin,colmax)`

This function crops all the images contained in a stack according to specific coordinates. It returns the new stack with the cropped images.

**Parameters:**  
- **img_stack : ndarray**  
3D array representing the stack of gray scaled images.

- **rowmin : int**  
The minimum row coordinate of the cropping region of interest.

- **rowmax : int**  
The maximum row coordinate of the cropping region of interest.

- **colmin : int**  
The minimum column coordinate of the cropping region of interest.

- **colmax : int**  
The maximum column coordinate of the cropping region of interest.

**Returns:**  
- **img_stack_cropped : ndarray**
3D array containig the cropped images.

**Raises:**  
- **ValueError**  
if **rowmin**>**rowmax** or **colmin**>**colmax**.


## `normalization (img_stack,dark_stack,flat_stack)`

This function computes the normalization of all the the images (tomographic projections) of a stack, using a stack of dark images and one of flat images. It returns the new stack or normalized images. The fuction used is the [neutompy.normalize_proj](https://neutompy-toolbox.readthedocs.io/en/latest/neutompy.preproc.preproc.html#normalize_proj), where the dose ROI and the crop ROI are not considered.

**Parameters:**  
- **img_stack : ndarray**  
3D array containing the projection images. 

- **dark_stack : ndarray**  
3D array containing the dark images.

- **flat_stack : ndarray**  
3D array containing the flat images.

**Returns:**  
- **img_stack_norm : ndarray**  
3D array containing the normalized images.

**Raises:**  
- **ValueError**  
if **img_stack**, **dark_stack** and **flat_stack** have different dimensions.

## `outliers_filter (img_stack, radius_2D_neighborhood, axis=0, k=1.0)`

This function removes bright or dark or both outliers from a stack of images.
The algorithm elaborates 2d images and the filtering is iterated over all images in the stack.
The function used is [neutompy.remove_outliers_stack](https://neutompy-toolbox.readthedocs.io/en/latest/neutompy.preproc.preproc.html#remove_outliers_stack) and it replaces a pixel by the median of the pixels in the 2d neighborhood if it deviates from the median by more than a certain value (k * threshold). Threshold is set to 0.02, while k is an optional parameter. This function uses the following formula:  

![fcorr1](https://latex.codecogs.com/svg.image?f_%7Bcorrected%7D(x,y)%20=%20w(x,y)%5Ccdot%20f_%7Boriginal%7D(x,y)%20&plus;%20(1-w(x,y))%5Ccdot%20f_%7Bmedian%7D(x,y))  

where *w* is 0 if the px value in (x,y) position deviates trom the median by more than k * threshold. Otherwise *w* is 1.  The user will be asked to choose the type of outliers to remove before the filtering.

**Parameters:**  
- **img_stack : ndarray**  
3D array containing the images to be filtered.

- **radius_2D_neighborhood : int or tuple of int**  
The radius of the 2D neighborhood. The radius is defined separately for each dimension as the number of pixels that the neighborhood extends outward from the center pixel.  
- **axis : int, optional**  
The axis along wich the outlier removal is iterated. Default value is 0.  

- **k : float, optional**  
A pixel is replaced by the median of the pixels in the neighborhood if it deviates from the median by more than k*threshold. Default value is 1.0.  

**Returns:**  
- **img_stack_filtered : ndarray**  
3D array containing the filtered images.

**Raises:**  
- **OSError**  
if the user input is different from 'b','B','d','D','a' or 'A'.

## **Correction**

## `find_shift_and_tilt_angle(y_of_ROIs,proj_0,proj_180)`

This function estimates the offset and the tilt angle of the sample rotation axis with respect to the detector using the projections at 0° and at 180°.
The latter is flipped horizontally and is compared with the projection at 0°, computing a root mean square error for each x position at each y coordinate considered. Hence the shift estimates for each y position are used to compute a polynomial fit of degree 1, obtaining the shift and the tilt angle of the axis of rotation. Some algebrical operations are performed on these final values for costruction.

References:  
[1](https://doi.org/10.1016/j.ndteint.2011.09.001) M. Yang, H. Gao, X. Li, F. Meng, D. Wei, *A new method todetermine the center of rotation shift in 2DCT scanning systemusing image cross correlation*, NDT&E International, Vol. 46 (2012), pp. 48-54.  
[2](https://doi.org/10.1016/j.nima.2011.01.129) Anders P. Kaestner,
*MuhRec—A new tomography reconstructor*,
Nuclear Instruments and Methods in Physics Research, Section A: Accelerators, Spectrometers, Detectors and Associated Equipment, Vol. 651, Issue 1, 2011, pp. 156-160.

**Parameters:**  
- **y_of_ROIs : ndarray**  
1D array of the y coordinates of the ROIs selected for the correction, with low noise and where the sample is visible.  

- **proj_0 : ndarray**  
2D array of the tomographic projection at 0°.  

- **proj_180 : ndarray**  
2D array of the tomographic projection at 180°.

**Returns:**  
- **m : float**  
slope of the polynomial fit between the shift and the corresponding y coordinate.  

- **q : float**  
intercept of the polynomial fit between the shift and the corresponding y coordinate.  

- **shift : ndarray**  
1D array containing the shift estimate for each y coordinate of **y_of_ROIs**.  

- **offset : float**  
shift of the axis of rotation with respect to the central vertical axis of the images.  

- **middle_shift : int**  
the offset value converted to integer.  

- **theta : float**  
the tilt angle of the rotation axis with respect to the central vertical axis of the images (in degrees).

**Raises:**  
- **ValueError**  
when the number of elements in **y_of_ROIs** is equal to 1, that is when the selected ROI has null height.





