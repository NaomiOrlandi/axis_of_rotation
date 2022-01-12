import argparse
import configparser
import sys
import os
import preparation_data
from show_stack import plot_tracker
import preprocess_and_correction


def parse_args ():
    description = 'Correction of rotation axis for tomographic projections'
    parser = argparse.ArgumentParser(description=description)
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

    config = configparser.ConfigParser()
    config.read('configuration.ini')


    filepath = config.get('directories','dirpath_tomo')         #path to the tomographic projections
    flatpath = config.get('directories','dirpath_flat')         #path to the flat image/es
    darkpath = config.get('directories','dirpath_dark')         #path to the dark image/es

    datapath = config.get('final files','dirpath_data')         #path for the data.txt file with coordinates of ROI, offset and tilt angle
    new_filepath = config.get('final files','filepath')         #path and the prefix of the name of the final files to be  saved in the specified folder
    digits = config.getint('final files','digits')              #number of digits to put in the final part of the final filenames to represent the index of the projections
                                                                #(ex. digit=4 -> filename_0000.tiff,filename_0001.tiff,...)

    last_angle = config.getint('angle','angle')                 #last angle of tomographic acquisition
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

    args = parse_args()

    print('> Reading the images...')
    #show all the images in the stack scrolling through them with arrow keys
    plot_tracker(tomo_stack)
    
    if args.roi and args.norm and args.out:
        '''
        In this case the cropping, the normalization
        and the outliers filtering of the images are performed.
        After the preprocessing, the shift and the tilt angle of 
        the axis of rotation of the sample with repsect to the 
        central vertical axis of the images are computed.
        So the user will be asked whether to correct or not the
        tomographic images. If yes, the new images will be saved in
        a specified path. If no, the rotation axis can be computed again.
        '''

        #preprocessing
        rowmin,rowmax,colmin,colmax = preprocess_and_correction.draw_ROI(tomo_0,'selection of ROI')
        preprocess_and_correction.save_ROI(rowmin,rowmax,colmin,colmax,datapath)
        tomo_stack_norm = preprocess_and_correction.normalization_with_ROI(tomo_stack,dark_stack,flat_stack,rowmin,rowmax,colmin,colmax)
        tomo_stack_norm_filtered = preprocess_and_correction.outliers_filter(tomo_stack_norm,radius_neighborhood)
        tomo_stack_norm_filtered_0,tomo_stack_norm_filtered_180 = preparation_data.projection_0_180(last_angle,tomo_stack_norm_filtered)
        
        #find axis and correction
        condition = True
        while condition:
            y_of_ROIs = preprocess_and_correction.ROIs_for_correction(tomo_stack_norm_filtered_0,ystep=5)
            m,q,shift,offset,middle_shift, theta = preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,tomo_stack_norm_filtered_0,tomo_stack_norm_filtered_180)
            preprocess_and_correction.graph_axis_rotation(tomo_stack_norm_filtered_0,tomo_stack_norm_filtered_180,y_of_ROIs,m,q,shift,offset,middle_shift, theta)
            
            ans= preprocess_and_correction.question()
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

        tomo_stack_corrected = preprocess_and_correction.correction_axis_rotation(tomo_stack_norm_filtered,middle_shift,theta,datapath)
        preprocess_and_correction.save_images(new_filepath,tomo_stack_corrected,digits)
        
    if args.roi and args.norm and not args.out:
        '''
        In this case the cropping and the normalization of the images
        are performed as preprocessing.
        After that, the shift and the tilt angle of 
        the axis of rotation of the sample with repsect to the 
        central vertical axis of the images are computed.
        So the user will be asked whether to correct or not the
        tomographic images. If yes, the new images will be saved in
        a specified path. If no, the rotation axis can be computed again.
        '''

        #preprocessing
        rowmin,rowmax,colmin,colmax = preprocess_and_correction.draw_ROI(tomo_0,'selection of ROI')
        preprocess_and_correction.save_ROI(rowmin,rowmax,colmin,colmax,datapath)
        tomo_stack_norm = preprocess_and_correction.normalization_with_ROI(tomo_stack,dark_stack,flat_stack,rowmin,rowmax,colmin,colmax)
        tomo_stack_norm_0, tomo_stack_norm_180 = preparation_data.projection_0_180(last_angle,tomo_stack_norm)
        
        #find axis and correction
        condition = True
        while condition:
            y_of_ROIs = preprocess_and_correction.ROIs_for_correction(tomo_stack_norm_0,ystep=5)
            m,q,shift,offset,middle_shift, theta = preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,tomo_stack_norm_0,tomo_stack_norm_180)
            preprocess_and_correction.graph_axis_rotation(tomo_stack_norm_0,tomo_stack_norm_180,y_of_ROIs,m,q,shift,offset,middle_shift, theta)
        
            ans= preprocess_and_correction.question()
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
        
        tomo_stack_corrected = preprocess_and_correction.correction_axis_rotation(tomo_stack_norm,middle_shift,theta,datapath)
        preprocess_and_correction.save_images(new_filepath,tomo_stack_corrected,digits)

    if args.roi and not args.norm and args.out:
        '''
        In this case the preprocessing consist in the cropping and
        outliers filtering of the images.
        After the preprocessing, the shift and the tilt angle of 
        the axis of rotation of the sample with repsect to the 
        central vertical axis of the images are computed.
        So the user will be asked whether to correct or not the
        tomographic images. If yes, the new images will be saved in
        a specified path. If no, the rotation axis can be computed again.
        '''

        #preprocessing
        rowmin,rowmax,colmin,colmax = preprocess_and_correction.draw_ROI(tomo_0,'selection of ROI')
        preprocess_and_correction.save_ROI(rowmin,rowmax,colmin,colmax,datapath)
        tomo_stack_crop = preprocess_and_correction.cropping(tomo_stack,rowmin,rowmax,colmin,colmax)
        tomo_stack_filtered = preprocess_and_correction.outliers_filter(tomo_stack_crop,radius_neighborhood)
        tomo_stack_filtered_0,tomo_stack_filtered_180 = preparation_data.projection_0_180(last_angle,tomo_stack_filtered)
        
        #find axis and correction
        condition = True
        while condition:
            y_of_ROIs = preprocess_and_correction.ROIs_for_correction(tomo_stack_filtered_0,ystep=5)
            m,q,shift,offset,middle_shift, theta = preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,tomo_stack_filtered_0,tomo_stack_filtered_180)
            preprocess_and_correction.graph_axis_rotation(tomo_stack_filtered_0,tomo_stack_filtered_180,y_of_ROIs,m,q,shift,offset,middle_shift, theta)
        
            ans= preprocess_and_correction.question()
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
        
        tomo_stack_corrected = preprocess_and_correction.correction_axis_rotation(tomo_stack_filtered,middle_shift,theta,datapath)
        preprocess_and_correction.save_images(new_filepath,tomo_stack_corrected,digits)

    if not args.roi and args.norm and args.out:
        '''
        In this case the the normalization
        and the outliers filtering of the images are performed.
        After the preprocessing, the shift and the tilt angle of 
        the axis of rotation of the sample with repsect to the 
        central vertical axis of the images are computed.
        So the user will be asked whether to correct or not the
        tomographic images. If yes, the new images will be saved in
        a specified path. If no, the rotation axis can be computed again.
        '''

        #preprocessing
        tomo_stack_norm = preprocess_and_correction.normalization_no_ROI(tomo_stack,dark_stack,flat_stack)
        tomo_stack_norm_filtered = preprocess_and_correction.outliers_filter(tomo_stack_norm,radius_neighborhood)
        tomo_stack_norm_filtered_0,tomo_stack_norm_filtered_180 = preparation_data.projection_0_180(last_angle,tomo_stack_norm_filtered)
        
        #find axis and correction
        condition = True
        while condition:
            y_of_ROIs = preprocess_and_correction.ROIs_for_correction(tomo_stack_norm_filtered_0,ystep=5)
            m,q,shift,offset,middle_shift, theta = preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,tomo_stack_norm_filtered_0,tomo_stack_norm_filtered_180)
            preprocess_and_correction.graph_axis_rotation(tomo_stack_norm_filtered_0,tomo_stack_norm_filtered_180,y_of_ROIs,m,q,shift,offset,middle_shift, theta)
        
            ans= preprocess_and_correction.question()
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

        tomo_stack_corrected = preprocess_and_correction.correction_axis_rotation(tomo_stack_norm_filtered,middle_shift,theta,datapath)
        preprocess_and_correction.save_images(new_filepath,tomo_stack_corrected,digits)

    if args.roi and not args.norm and not args.out:
        '''
        In this case the preprocessing is the cropping of images.
        After that, the shift and the tilt angle of 
        the axis of rotation of the sample with repsect to the 
        central vertical axis of the images are computed.
        So the user will be asked whether to correct or not the
        tomographic images. If yes, the new images will be saved in
        a specified path. If no, the rotation axis can be computed again.
        '''

        #preprocessing
        rowmin,rowmax,colmin,colmax = preprocess_and_correction.draw_ROI(tomo_0,'selection of ROI')
        preprocess_and_correction.save_ROI(rowmin,rowmax,colmin,colmax,datapath)
        tomo_stack_crop = preprocess_and_correction.cropping(tomo_stack,rowmin,rowmax,colmin,colmax)
        tomo_stack_crop_0,tomo_stack_crop_180 = preparation_data.projection_0_180(last_angle,tomo_stack_crop)
        
        #find axis and correction
        condition = True
        while condition:
            y_of_ROIs = preprocess_and_correction.ROIs_for_correction(tomo_stack_crop_0,ystep=5)
            m,q,shift,offset,middle_shift, theta = preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,tomo_stack_crop_0,tomo_stack_crop_180)
            preprocess_and_correction.graph_axis_rotation(tomo_stack_crop_0,tomo_stack_crop_180,y_of_ROIs,m,q,shift,offset,middle_shift, theta)
        
            ans= preprocess_and_correction.question()
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
        
        tomo_stack_corrected = preprocess_and_correction.correction_axis_rotation(tomo_stack_crop,middle_shift,theta,datapath)
        preprocess_and_correction.save_images(new_filepath,tomo_stack_corrected)

    if not args.roi and args.norm and not args.out:
        '''
        In this case the normalization of images is performed.
        After the preprocessing, the shift and the tilt angle of 
        the axis of rotation of the sample with repsect to the 
        central vertical axis of the images are computed.
        So the user will be asked whether to correct or not the
        tomographic images. If yes, the new images will be saved in
        a specified path. If no, the rotation axis can be computed again.
        '''

        #preprocessing
        tomo_stack_norm = preprocess_and_correction.normalization_no_ROI(tomo_stack,dark_stack,flat_stack)
        tomo_stack_norm_0, tomo_stack_norm_180 = preparation_data.projection_0_180(last_angle,tomo_stack_norm)
        
        #find axis and correction
        condition = True
        while condition:
            y_of_ROIs = preprocess_and_correction.ROIs_for_correction(tomo_stack_norm_0,ystep=5)
            m,q,shift,offset,middle_shift, theta = preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,tomo_stack_norm_0,tomo_stack_norm_180)
            preprocess_and_correction.graph_axis_rotation(tomo_stack_norm_0,tomo_stack_norm_180,y_of_ROIs,m,q,shift,offset,middle_shift, theta)
        
            ans= preprocess_and_correction.question()
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
        
        tomo_stack_corrected = preprocess_and_correction.correction_axis_rotation(tomo_stack_norm,middle_shift,theta,datapath)
        preprocess_and_correction.save_images(new_filepath,tomo_stack_corrected,digits)

    if not args.roi and not args.norm and args.out:
        '''
        In this case the outliers filtering of images in performed
        as preprocessing.
        After that, the shift and the tilt angle of 
        the axis of rotation of the sample with repsect to the 
        central vertical axis of the images are computed.
        So the user will be asked whether to correct or not the
        tomographic images. If yes, the new images will be saved in
        a specified path. If no, the rotation axis can be computed again.
        '''

        #preprocessing
        tomo_stack_filtered = preprocess_and_correction.outliers_filter(tomo_stack,radius_neighborhood)
        tomo_stack_filtered_0,tomo_stack_filtered_180 = preparation_data.projection_0_180(last_angle,tomo_stack_filtered)
        
        #find axis and correction
        condition = True
        while condition:
            y_of_ROIs = preprocess_and_correction.ROIs_for_correction(tomo_stack_filtered_0,ystep=5)
            m,q,shift,offset,middle_shift, theta = preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,tomo_stack_filtered_0,tomo_stack_filtered_180)
            preprocess_and_correction.graph_axis_rotation(tomo_stack_filtered_0,tomo_stack_filtered_180,y_of_ROIs,m,q,shift,offset,middle_shift, theta)
        
            ans= preprocess_and_correction.question()
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
        
        tomo_stack_corrected = preprocess_and_correction.correction_axis_rotation(tomo_stack_filtered,middle_shift,theta,datapath)
        preprocess_and_correction.save_images(new_filepath,tomo_stack_corrected,digits)

    if not args.roi and not args.norm and not args.out:
        '''
        In this case no preprocessing is performed on the tomographic images.
        Here the first step is the computation of the shift and 
        the tilt angle of the axis of rotation of the sample with repsect to the 
        central vertical axis of the images.
        The user will be asked whether to correct or not the
        tomographic images. If yes, the new images will be saved in
        a specified path. If no, the rotation axis can be computed again.
        '''
        
        #find axis and correction
        condition = True
        while condition:
            y_of_ROIs = preprocess_and_correction.ROIs_for_correction(tomo_0,ystep=5)
            m,q,shift,offset,middle_shift, theta = preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,tomo_0,tomo_180)
            preprocess_and_correction.graph_axis_rotation(tomo_0,tomo_180,y_of_ROIs,m,q,shift,offset,middle_shift, theta)
        
            ans= preprocess_and_correction.question()
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
        
        tomo_stack_corrected = preprocess_and_correction.correction_axis_rotation(tomo_stack,middle_shift,theta,datapath)
        preprocess_and_correction.save_images(new_filepath,tomo_stack_corrected,digits)


if __name__ == '__main__':
    main()










