This library contains all the functions in which the user interact with the program.
[Source of the file](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/COR/user_interaction.py)

## `draw_ROI (img,title,ratio=0.85)`

This function allows to select interactively a rectangular a region of interest (ROI) on an image and returns the coordinates of the ROI. The ROI should have width and height greater than zero to be selected.

**Parameters:**  
- **img : ndarray**  
2D array representing the image.

- **title : str**  
title of the window where the user will select the ROI.

- **ratio : float,optional**
The filling ratio of the window respect to the screen resolution.
It must be a number between 0 and 1. The default value is 0.85.

**Returns:**
- **rowmin : int**  
The minimum row coordinate.

- **rowmax : int**  
The maximum row coordinate.

- **colmin : int**  
The minimum column coordinate.

- **colmax : int**  
The maximum column coordinate.

**Raises:**
- **ValueError**  
if ratio is not greater than 0 and less or equal to 1.

- **ValueError**  
if img is not a 2D array.


## `ROIs_for_correction(ref_proj,ystep=5)`

This function allows to select one or multiple ROIs in the projections that will be considered when searching for the axis of rotation offset and tilt angle in the function [*find_shift_and_tilt_angle*](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/documentation_functions/preprocess_and_correction.md).
The suggestion is to select the regions where the sample is visible and where there is as little noise as possible.
The method returns a 1D array containing the values of y coordinates
selected in the ROIs with a step defined by ystep.

**Parameters:**  
- **ref_proj : ndarray**  
2D array representing the image where the user will select the ROIs.

- **ystep : int, optional**  
The step between two successive y coordinates in the returned array.

**Returns:**
- **y_of_ROIs : ndarray**  
1D array containing the y coordinates included in the selected ROIs.

## `graph_axis_rotation (proj_0,proj_180,y_of_ROIs,m,q,shift,offset,middle_shift,theta)`

This function shows two figures that report the results of  [*find_shift_and_tilt_angle*](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/documentation_functions/preprocess_and_correction.md) function. In the first figure are shown the computed shift of the rotation axis from the polynomial fit and the subtraction between the projection at 0° and the horizontal flip of the projection at 180° (**proj_0** - **pro_180_[:,::-1]**) before the correction. 
The second figure shows the difference image (**proj_0** - **pro_180[:,::-1]**) after the correction and the histogram of the square of residuals between **proj_0** and the filpped **proj_180**.

**Parameters:**  
- **proj_0 : ndarray**  
2D array of the tomographic projection at 0°.  

- **proj_180 : ndarray**  
2D array of the tomographic projection at 180°.  

- **y_of_ROIs : ndarray**  
1D array of the y coordinates of the ROIs selected for the correction, with low noise and where the sample is visible.  

- **m : float**  
slope of the polynomial fit between the shift and the corresponding y coordinate
(see *find_shift_and_tilt_angle* function).  

- **q : float**  
intercept of the polynomial fit between the shift and the corresponding y coordinate (see *find_shift_and_tilt_angle* function).  

- **shift : ndarray**  
1D array containing the shift estimate for each y coordinate of **y_of_ROIs** (see *find_shift_and_tilt_angle* function).  

- **offset : float**  
shift of the axis of rotation with respect to the central vertical axis of the images (in px).

- **middle_shift : int**  
the offset value converted to integer.  

- **theta : float**  
the tilt angle of the rotation axis with respect to the central vertical axis of the images (in degrees).

## `correction_axis_rotation (img_stack,shift,theta,datapath)`

This function performs the correction of all the images in the stack, according to the shift and tilt angle of the axis of rotation with respect to the central vertical axis of the images. The method also open the file *data.txt* placed in the path expressed by **datapath** and write there the values of the shift and the tilt angle of the axis of rotation. Finally it returns the stack of corrected images.

**Parameters:**  
- **img_stack : ndarray**  
3D array containing the tomographic projection images to correct.  

- **shift : int**  
shift of the axis of rotation with respect to the central vertical axis of the images (in px).  

- **theta : float**  
the tilt angle of the rotation axis with respect to the central vertical axis of the images (in degrees).  

- **datapath : str**  
string representing the directory path where *data.txt* is placed.

**Returns:**  
- **img_stack : ndarray**  
3D array containing the corrected tomographic images.
