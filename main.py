import argparse
import configparser
import numpy as np
import cv2
import glob


def parse_args ():
    description = 'Correction of rotation axis for tomographic projections'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-drawROI',
                         dest='roi',
                         action= 'store_true',
                         required=False,
                         help='draw a ROI in an image in the stack to use for all the other processes')
    parser.add_argument('-norm',
                         dest='norm',
                         action= 'store_true',
                         required=False,
                         help='normalization of all images in the stack')
    parser.add_argument('-outliers',
                         dest='out',
                         action= 'store_true',
                         required=False,
                         help='outliers filter is applied to all images in the stack')
    parser.add_argument('-findaxis',
                         dest='find',
                         action= 'store_true',
                         required=False,
                         help='the offset and the tilt angle of the rotation axis is found with respect to the ccentral axis of the detector')



config = configparser.ConfigParser()
config.read('paths.ini')

   #create an empty image list

filepath = config.get('directories','dirpath_tomo')+'/*.tiff'   #path to the tomographic projections
flatpath = config.get('directories','dirpath_flat')+'/*.tiff'   #path to the flat image/es
darkpath = config.get('directories','dirpath_dark')+'/*.tiff'   #path to the dark image/es
last_angle = config.getint('angle','angle')

def reader_gray_images (filepath):
    global image_list
    image_list = []
    for filename in glob.glob(filepath): 
        im=cv2.imread(filename,0) #0 stands for the gray_image reading (default is RGB reading)
        image_list.append(im)
    return image_list
#create an array for the stack of tomographic projections

projections = np.asarray(image_list)

#create an array for the stack of flat images and one for the dark images
#the falt_stack has the same dimensions of the projections stack, hence if you have one flat image, it is replicated to fill the ndarray
#the same for the dark_stack



#define tomographic projections at angle 0 and 180 degrees
#projection_180 is the method to find the projection at 180 degree when the last angle is 180 or 360 degrees
def projection_180 (angle):
    if angle == 360:
        proj_180 = projections[int(projections.shape[0]/2),:,:]
        return proj_180
    elif angle == 180:
        proj_180 = projections[int(projections.shape[0]),:,:]
        return proj_180


proj_0 = projections[0,:,:]
proj_180 = projection_180(last_angle)




