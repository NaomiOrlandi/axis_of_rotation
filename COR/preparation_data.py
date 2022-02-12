import cv2
import glob
import numpy as np
import os

#reader of the images that returns a list of images
def reader_gray_images (filepath):
    '''
    This function reads the .tiff gray scaled images contained in the directory
    whose path is expressed by filepath and returns a list of two dimensional
    arrays representing the images
    
    Parameters
    ----------
    filepath : str
        path to the directory containing the .tiff files
        
    Returns
    -------
    image_list : list
        list of 2D arrays representing the read images
    
    Raises
    ------
    OSError
        when the directory does not contain any .tiff file
    OSError
        when the directory does not exist
    '''
    image_list = []
    files = os.path.join(filepath,'*.tiff')

    if os.path.isdir(filepath):
        for filename in glob.glob(files): 
            im=cv2.imread(filename,flags=(cv2.IMREAD_GRAYSCALE | cv2.IMREAD_ANYDEPTH)) #0 stands for the gray_image reading (default is RGB reading)
            image_list.append(im)
        if len(image_list)==0:
            raise OSError('directory {0} does not contain any .tiff file'.format(filepath))
        else:
            return image_list
        
    else:
        raise OSError('directory {0} does not exist'.format(filepath))
    

#image list is transformed in a 3D array
def create_array (img_list,img_list_tomo):
    '''
    This function transforms a list of two dimensional arrays 
    (representing gray scaled images) into a three dimensional array.
    The number of elements in the list can be 1 or the same of
    another list taken as a reference.
    In the first case a 3D array is created using the same image repeated
    untill reaching the required dimension.
    In the second case the list is simply converted into a 3D array.
    
    Parameters
    ----------
    img_list : list
        list of 2D arrays that has to be converted to a 3D array
    img_list_tomo : list
        list of 2D array taken as reference

    Returns
    -------
    img_array : ndarray
        3D array with the same dimensions of img_list_tomo converted to an array

    Raises
    ------
    ValueError
        when img_list contains a num of elements different from 1 or the num of elements of img_list_tomo
    ValueError
        when the dimensions of the 2D arrays of img_list are different from the ones of the 2D arrays of img_list_tomo 
    '''
    im_dim = np.array(img_list[0]).shape
    tomo_dim = np.array(img_list_tomo[0]).shape
    if im_dim == tomo_dim:
        if len(img_list) == len(img_list_tomo):
            img_array = np.asarray(img_list, dtype=np.float32)
            return img_array
        elif len(img_list) == 1:
            tomo_array = np.asarray(img_list_tomo)
            img_array = np.full(tomo_array.shape,img_list, dtype=np.float32)
            return img_array
        elif len(img_list) !=1 and len(img_list) != len(img_list_tomo):
            raise ValueError('{0} should contain or 1 image or an amount of images equal to the num of tomographic projections'.format(img_list))
    else:
        raise ValueError('{0} should contain images with the same dimensions of tomographic projections'.format(img_list))



#define tomographic projections at angle 0 and 180 degrees
def projection_0_180 (angle,img_array):
    '''
    This function takes a stack of images and returns the first one
    and the last or the middle one, depending if the tomographic 
    acquisition is performed with a maximum angle rispectively of 180° or 360°.
    
    Parameters
    ----------
    angle : int
        integer representing the last angle of acquisition
    img_array : ndarray
        3D array representing the stack of images acquired
    
    Returns
    -------
    proj_0 : ndarray
        2D array representing the first image of the stack
    proj_180 : ndarray
        2D array representing the image acquired at the angle 180°
    
    Raises
    ------
    ValueError
        when angle is different from 180 or 360
    '''
    proj_0 = img_array[0,:,:]
    if angle == 360:
        proj_180 = img_array[int(((img_array.shape[0]-1)/2)),:,:]
        return proj_0,proj_180
    elif angle == 180:
        proj_180 = img_array[int(img_array.shape[0]-1),:,:]
        return proj_0,proj_180
    else:
        raise ValueError('the maximum angle for the tomography must be 180 or 360 degrees')
    