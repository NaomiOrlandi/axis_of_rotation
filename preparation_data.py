import cv2
import glob
import numpy as np
import os

#reader of the images that returns a list of images
def reader_gray_images (filepath):
    image_list = []
    files = os.path.join(filepath,'*.tiff')

    if os.path.isdir(filepath):
        for filename in glob.glob(files): 
            im=cv2.imread(filename,cv2.IMREAD_GRAYSCALE) #0 stands for the gray_image reading (default is RGB reading)
            image_list.append(im)
        return image_list
    else:
        raise ImportError('directory {0} does not exist'.format(filepath))
    

#image list is transformed in a 3D array
def create_array (img_list,img_list_tomo):
    im_dim = np.array(img_list[0]).shape
    tomo_dim = np.array(img_list_tomo[0]).shape
    if im_dim == tomo_dim:
        if len(img_list) == len(img_list_tomo):
            img_array = np.asarray(img_list)
            return img_array
        elif len(img_list) == 1:
            tomo_array = np.asarray(img_list_tomo)
            img_array = np.full(tomo_array.shape,img_list)
            return img_array
        elif len(img_list) !=1 and len(img_list) != len(img_list_tomo):
            raise ValueError('{0} should contain or 1 image or an amount of images equal to the num of tomographic projections'.format(img_list))
    else:
        raise ValueError('{0} should contain images with the same dimensions of tomographic projections'.format(img_list))



#define tomographic projections at angle 0 and 180 degrees
def projection_0_180 (angle,img_array):
    proj_0 = img_array[0,:,:]
    if angle == 360:
        proj_180 = img_array[int((img_array.shape[0]/2)-1),:,:]
    elif angle == 180:
        proj_180 = img_array[int(img_array.shape[0]-1),:,:]
    return proj_0,proj_180
    