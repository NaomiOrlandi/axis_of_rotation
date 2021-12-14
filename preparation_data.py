import cv2
import glob
import numpy as np

#reader of the images that returns a list of images
def reader_gray_images (filepath):
    image_list = []
    for filename in glob.glob(filepath): 
        im=cv2.imread(filename,0) #0 stands for the gray_image reading (default is RGB reading)
        image_list.append(im)
    return image_list

#image list is transformed in a 3D array
def create_array (img_list,img_list_tomo):
    if len(img_list) == len(img_list_tomo):
        img_array = np.asarray(img_list)
        return img_array
    elif len(img_list) == 1:
        tomo_array = np.asarray(img_list)
        img_array = np.full(tomo_array.shape,img_list)
        return img_array




#define tomographic projections at angle 0 and 180 degrees
def projection_0_180 (angle,img_array):
    if angle == 360:
        proj_180 = img_array[int(img_array.shape[0]/2),:,:]
        return proj_180
    elif angle == 180:
        proj_180 = img_array[int(img_array.shape[0]),:,:]
        return proj_180
    proj_0 = img_array[0,:,:]
    return proj_0
    