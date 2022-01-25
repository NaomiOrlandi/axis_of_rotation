import argparse
import configparser
import sys
import os
import preparation_data
from show_stack import plot_tracker
import preprocess_and_correction
import user_interaction


def parse_args ():
    description = 'Correction of rotation axis for tomographic projections'
    parser = argparse.ArgumentParser(description=description)

    #positional argument
    parser.add_argument('config_file', help='path of the configuration file')

    #optional arguments
    parser.add_argument('-roi',
                         dest='roi',
                         action= 'store_true',
                         required=False,
                         help='draw a region of interest (ROI) on an image of the stack for cropping all the images')
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

    args = parse_args()

    config = configparser.ConfigParser()

    if os.path.isfile(args.config_file):
        config.read(str(args.config_file))
    else:
        raise OSError ('file {0} does not exist'.format(args.config_file))


    filepath = config.get('directories','dirpath_tomo')         #path to the tomographic projections
    flatpath = config.get('directories','dirpath_flat')         #path to the flat image/es
    darkpath = config.get('directories','dirpath_dark')         #path to the dark image/es

    datapath = config.get('final files','dirpath_data')         #path for the data.txt file with coordinates of ROI, offset and tilt angle
    new_filepath = config.get('final files','filepath')         #path and the prefix of the name of the final files to be  saved in the specified folder
    digits = config.getint('final files','digits')              #number of digits to put in the final part of the final filenames to represent the index of the projections
                                                                #(ex. digit=4 -> filename_0000.tiff,filename_0001.tiff,...)

    last_angle = config.getint('angle','angle')                 #last angle of tomographic acquisition
    
    if args.out:                                                #read neighborhood radius only if outlier filter is required
        radius_neighborhood = config.getint('outlier filter','radius_neighborhood') #neighborhood radius for outlier filtering


    #lists of images
    tomo_list = preparation_data.reader_gray_images(filepath)
    flat_list = preparation_data.reader_gray_images(flatpath)
    dark_list = preparation_data.reader_gray_images(darkpath)


    #3D arrays of images
    tomo_stack = preparation_data.create_array(tomo_list,tomo_list)
    flat_stack = preparation_data.create_array(flat_list,tomo_list)
    dark_stack = preparation_data.create_array(dark_list,tomo_list)

    #projection at 0° and at 180°
    tomo_0,tomo_180 = preparation_data.projection_0_180(last_angle,tomo_stack)

    

    print('> Reading the images...')
    #show all the images in the stack scrolling through them with arrow keys
    plot_tracker(tomo_stack)


    #cropping
    if args.roi:
        rowmin,rowmax,colmin,colmax = user_interaction.draw_ROI(tomo_0,'selection of ROI')
        preprocess_and_correction.save_ROI(rowmin,rowmax,colmin,colmax,datapath)
        print('> Tomographic projections:')
        tomo_stack_preproc = preprocess_and_correction.cropping(tomo_stack,rowmin,rowmax,colmin,colmax)
        
        #normalization and outliers filter (cropping)
        if args.norm:
            print('> Dark images:')
            dark_stack_crop = preprocess_and_correction.cropping(dark_stack,rowmin,rowmax,colmin,colmax)
            print('> Flat images:')
            flat_stack_crop = preprocess_and_correction.cropping(flat_stack,rowmin,rowmax,colmin,colmax)
            tomo_stack_preproc = preprocess_and_correction.normalization(tomo_stack_preproc, dark_stack_crop, flat_stack_crop)
            
            if args.out:
                tomo_stack_preproc = preprocess_and_correction.outliers_filter(tomo_stack_preproc,radius_neighborhood)
        
        #outliers filter (cropping)
        elif args.out:
            tomo_stack_preproc = preprocess_and_correction.outliers_filter(tomo_stack_preproc,radius_neighborhood)
    
    #no cropping
    #normalization
    elif args.norm:
        tomo_stack_preproc = preprocess_and_correction.normalization(tomo_stack, dark_stack, flat_stack)
        
        #normalization and outlierss filter
        if args.out:
            tomo_stack_preproc = preprocess_and_correction.outliers_filter(tomo_stack_preproc,radius_neighborhood)
    
    #outliers filter
    elif args.out:
        tomo_stack_preproc = preprocess_and_correction.outliers_filter(tomo_stack,radius_neighborhood)


    #select projections at 0° and 180°
    tomo_stack_preproc_0, tomo_stack_preproc_180 = preparation_data.projection_0_180(last_angle,tomo_stack_preproc)

#find axis and correction
    condition = True
    while condition:
        y_of_ROIs = user_interaction.ROIs_for_correction(tomo_stack_preproc_0,ystep=5)
        m,q,shift,offset,middle_shift, theta = preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,tomo_stack_preproc_0,tomo_stack_preproc_180)
        user_interaction.graph_axis_rotation(tomo_stack_preproc_0,tomo_stack_preproc_180,y_of_ROIs,m,q,shift,offset,middle_shift, theta)
        
        ans= user_interaction.user_choice_for_correction()
        if(ans=='Y' or ans=='y'):
            condition = False
            break
        elif(ans=='N' or ans=='n'):
            condition = True
        elif(ans=='C' or ans=='c'):
            print('> Script aborted.')
            if os.path.exists(os.path.join(datapath,"data.txt")):  #remove data.txt file if it exists
                os.remove(os.path.join(datapath,"data.txt"))
                sys.exit()
            else:
                sys.exit()
        else:
            print('Input not valid.')

    tomo_stack_corrected = preprocess_and_correction.correction_axis_rotation(tomo_stack_preproc,middle_shift,theta,datapath)
    preprocess_and_correction.save_images(new_filepath,tomo_stack_corrected,digits)



if __name__ == '__main__':
    main()










