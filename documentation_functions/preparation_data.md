# **Preparation_data.py**

This library contains all the functions for an initial data elaboration in order to obtain all the needed information for a further analysis (preprocessing and correction of images). [Source of the file](https://github.com/NaomiOrlandi/axis_of_rotation/blob/main/COR/preparation_data.py)

## `reader_gray_images (filepath)`

This function reads the .tiff gray scaled images (tomographic projections) contained in the directory, whose path is expressed by filepath and returns a list of two dimensional arrays representing the images. 

**Parameters:**
- **filepath : str**  
path to the directory containing the .tiff files.

**Returns:**
- **image_list : list**  
list of 2D arrays representing the read images.

**Raises:**
- **ImportError**  
when the directory does not contain any .tiff file.
- **ImportError**  
when the directory does not exist.

## `create_array (img_list,img_list_tomo)`

This function transforms a list of two dimensional arrays (representing gray scaled images) into a three dimensional array. The number of elements in the list can be 1 or the same of another list taken as a reference. In the first case a 3D array is created using the same image repeated untill reaching the required dimension. In the second case the list is simply converted into a 3D array.

**Parameters:**
- **img_list : list**  
list of 2D arrays. It has to be converted to a 3D array. 

- **img_list_tomo : list**  
list of 2D array taken as reference.

**Returns:**
- **img_array : ndarray**  
3D array with the same dimensions of **img_list_tomo** converted to an array.

**Raises:**
- **ValueError**  
when **img_list** contains a num of elements different from 1 or the num of elements of **img_list_tomo**.
- **ValueError**  
when the dimensions of the 2D arrays of **img_list** are different from the ones of the 2D arrays of **img_list_tomo**.

## `projection_0_180 (angle,img_array)`

This function takes a stack of images and returns the first one and the last or the middle one, depending if the tomographic acquisition is performed with a maximum angle rispectively of 180° or 360°.

**Parameters:**  
- **angle : int**  
integer representing the last angle of acquisition.
- **img_array : ndarray**  
3D array representing the stack of acquired images.

**Returns:**  
- **proj_0 : ndarray**  
2D array representing the first image of the stack.
- **proj_180 : ndarray**  
2D array representing the image acquired at the angle 180°.

**Raises:**
- **ValueError**  
when **angle** is different from 180 or 360.

