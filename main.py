import argparse
import configparser
from sys import argv
from matplotlib.pyplot import plot
import numpy as np
import cv2
import glob
import preparation_data
import os
from image_slicer import plot_tracker
import preprocessing_and_COR


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
    
    args = parser.parse_args()
    return args

def main ():
    config = configparser.ConfigParser()
    config.read('paths.ini')


    filepath = config.get('directories','dirpath_tomo')   #path to the tomographic projections
    flatpath = config.get('directories','dirpath_flat')   #path to the flat image/es
    darkpath = config.get('directories','dirpath_dark')   #path to the dark image/es

    datapath = config.get('final files','dirpath_data') #path for the data.txt file with coordinates of ROI, offset and tilt angle
    new_filepath = config.get('final files','filepath') #path and the prefix of the name of the final files to be  saved in the specified folder
    digits = config.getint('final files','digits') #number of digits to put in the final part of the final filenames to represent the index of the projections (ex. digit=4 -> filename_0000.tiff,filename_0001.tiff,...)

    last_angle = config.getint('angle','angle')
    radius_neighborhood = config.getint('outlier filter','radius_neighborhood')
    #print(filepath,flatpath,darkpath)



    #lists of images
    tomo_list = preparation_data.reader_gray_images(filepath)
    flat_list = preparation_data.reader_gray_images(flatpath)
    dark_list = preparation_data.reader_gray_images(darkpath)

    print(len(tomo_list))#,len(flat_list),len(dark_list))

    #3D arrays of images
    tomo_stack = preparation_data.create_array(tomo_list,tomo_list)
    flat_stack = preparation_data.create_array(flat_list,tomo_list)
    dark_stack = preparation_data.create_array(dark_list,tomo_list)

    print(tomo_stack.shape,flat_stack.shape,dark_stack.shape)
    plot_tracker(tomo_stack)

    tomo_0,tomo_180 = preparation_data.projection_0_180(last_angle,tomo_stack)

    args = parse_args()
    
    if args.roi and args.norm and args.out:

        rowmin,rowmax,colmin,colmax = preprocessing_and_COR.draw_ROI(tomo_0,datapath)
        tomo_stack_norm = preprocessing_and_COR.normalization_with_ROI(tomo_stack,dark_stack,flat_stack,rowmin,rowmax,colmin,colmax)
        tomo_stack_norm_filtered = preprocessing_and_COR.outliers_filter(tomo_stack_norm,radius_neighborhood)
        tomo_stack_norm_filtered_0,tomo_stack_norm_filtered_180 = preparation_data.projection_0_180(last_angle,tomo_stack_norm_filtered)
        tomo_stack_corrected = preprocessing_and_COR.correct_images(tomo_stack_norm_filtered,tomo_stack_norm_filtered_0,tomo_stack_norm_filtered_180,datapath)
        preprocessing_and_COR.save_images(new_filepath,tomo_stack_corrected,digits)
        
    if args.roi and args.norm and not args.out:
        rowmin,rowmax,colmin,colmax = preprocessing_and_COR.draw_ROI(tomo_0,datapath)
        tomo_stack_norm = preprocessing_and_COR.normalization_with_ROI(tomo_stack,dark_stack,flat_stack,rowmin,rowmax,colmin,colmax)
        tomo_stack_norm_0, tomo_stack_norm_180 = preparation_data.projection_0_180(last_angle,tomo_stack_norm)
        tomo_stack_corrected = preprocessing_and_COR.correct_images(tomo_stack_norm,tomo_stack_norm_0,tomo_stack_norm_180,datapath)
        preprocessing_and_COR.save_images(new_filepath,tomo_stack_corrected,digits)

    if args.roi and not args.norm and args.out:
        rowmin,rowmax,colmin,colmax = preprocessing_and_COR.draw_ROI(tomo_0,datapath)
        tomo_stack_crop = preprocessing_and_COR.cropping(tomo_stack,rowmin,rowmax,colmin,colmax)
        tomo_stack_filtered = preprocessing_and_COR.outliers_filter(tomo_stack_crop,radius_neighborhood)
        tomo_stack_filtered_0,tomo_stack_filtered_180 = preparation_data.projection_0_180(last_angle,tomo_stack_filtered)
        tomo_stack_corrected = preprocessing_and_COR.correct_images(tomo_stack_filtered,tomo_stack_filtered_0,tomo_stack_filtered_180,datapath)
        preprocessing_and_COR.save_images(new_filepath,tomo_stack_corrected,digits)

    if not args.roi and args.norm and args.out:
        tomo_stack_norm = preprocessing_and_COR.normalization_no_ROI(tomo_stack,dark_stack,flat_stack)
        tomo_stack_norm_filtered = preprocessing_and_COR.outliers_filter(tomo_stack_norm,radius_neighborhood)
        tomo_stack_norm_filtered_0,tomo_stack_norm_filtered_180 = preparation_data.projection_0_180(last_angle,tomo_stack_norm_filtered)
        tomo_stack_corrected = preprocessing_and_COR.correct_images(tomo_stack_norm_filtered,tomo_stack_norm_filtered_0,tomo_stack_norm_filtered_180,datapath)
        preprocessing_and_COR.save_images(new_filepath,tomo_stack_corrected,digits)

    if args.roi and not args.norm and not args.out:
        rowmin,rowmax,colmin,colmax = preprocessing_and_COR.draw_ROI(tomo_0,datapath)
        tomo_stack_crop = preprocessing_and_COR.cropping(tomo_stack,rowmin,rowmax,colmin,colmax)
        tomo_stack_crop_0,tomo_stack_crop_180 = preparation_data.projection_0_180(last_angle,tomo_stack_crop)
        tomo_stack_corrected = preprocessing_and_COR.correct_images(tomo_stack_crop,tomo_stack_crop_0,tomo_stack_crop_180,datapath)
        preprocessing_and_COR.save_images(new_filepath,tomo_stack_corrected)

    if not args.roi and args.norm and not args.out:
        tomo_stack_norm = preprocessing_and_COR.normalization_no_ROI(tomo_stack,dark_stack,flat_stack)
        tomo_stack_norm_0, tomo_stack_norm_180 = preparation_data.projection_0_180(last_angle,tomo_stack_norm)
        tomo_stack_corrected = preprocessing_and_COR.correct_images(tomo_stack_norm,tomo_stack_norm_0,tomo_stack_norm_180,datapath)
        preprocessing_and_COR.save_images(new_filepath,tomo_stack_corrected,digits)

    if not args.roi and not args.norm and args.out:
        tomo_stack_filtered = preprocessing_and_COR.outliers_filter(tomo_stack,radius_neighborhood)
        tomo_stack_filtered_0,tomo_stack_filtered_180 = preparation_data.projection_0_180(last_angle,tomo_stack_filtered)
        tomo_stack_corrected = preprocessing_and_COR.correct_images(tomo_stack_filtered,tomo_stack_filtered_0,tomo_stack_filtered_180,datapath)
        preprocessing_and_COR.save_images(new_filepath,tomo_stack_corrected,digits)

if __name__ == '__main__':
    main()










