import argparse
import configparser
import numpy as np
import cv2
import glob
import preparation_data
import os

'''
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
    args = parser.parse_args()
    return args
'''
def main ():
    config = configparser.ConfigParser()
    config.read('paths.ini')

    #args = parse_args()


    filepath = os.path.join(config.get('directories','dirpath_tomo'),'*.tiff')   #path to the tomographic projections
    flatpath = os.path.join(config.get('directories','dirpath_flat'),'*.tiff')   #path to the flat image/es
    darkpath = os.path.join(config.get('directories','dirpath_dark'),'*.tiff')   #path to the dark image/es
    last_angle = config.getint('angle','angle')

    print(filepath,flatpath,darkpath)

    
    

    #lists of images
    tomo_list = preparation_data.reader_gray_images(filepath)
    flat_list = preparation_data.reader_gray_images(flatpath)
    dark_list = preparation_data.reader_gray_images(darkpath)

    print(len(tomo_list),len(flat_list),len(dark_list))

    #3D arrays of images
    tomo_stack = preparation_data.create_array(tomo_list,tomo_list)
    flat_stack = preparation_data.create_array(flat_list,tomo_list)
    dark_stack = preparation_data.create_array(dark_list,tomo_list)

    print(tomo_stack.shape,flat_stack.shape,dark_stack.shape)

if __name__ == '__main__':
    main()










