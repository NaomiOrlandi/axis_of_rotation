import sys
sys.path.insert(0,".\\COR")
import pytest
from COR import preparation_data
from COR import preprocess_and_correction
import numpy as np
import math
from unittest import mock
import cv2
from hypothesis import given
from hypothesis import settings
import hypothesis.strategies as st
from hypothesis.extra.numpy import arrays



#strategy for the elements of arrays (floats)
array_elements = st.floats(min_value=1,max_value=250,allow_nan=False, allow_infinity=False,width=32)
array_elements_dark = st.floats(min_value=1,max_value=10,allow_nan=False, allow_infinity=False,width=32)
array_elements_flat = st.floats(min_value=250,max_value=255,allow_nan=False, allow_infinity=False,width=32)
#strategy for a 2D array (10x10)
array_2D = arrays(float,(10,10),elements=array_elements,fill=st.nothing())


#strategy for list of 2 different sorted random integers in [0,4]
list_rows = st.lists(st.integers(0,4),min_size=2,max_size=2).map(sorted).filter(lambda x : x[0] < x[1])
list_columns = st.lists(st.integers(0,4),min_size=2,max_size=2).map(sorted).filter(lambda x : x[0] < x[1])
#strategy for a list of 2 different sorted random integers in [0,9], used to select a ROI od array_2D
list_yROI = st.lists(st.integers(0,9),min_size=2,max_size=2).map(sorted).filter(lambda x : x[0] < x[1])


#strategies for 3D array (5x5x5) with floats in [1,250]
array_projections = arrays(np.float32,([5,5,5]),elements=array_elements,fill=st.nothing())
#strategies for 3D array (5x5x5) with floats in [250,255]
array_flat = arrays(np.float32,([5,5,5]),elements=array_elements_flat,fill=st.nothing())
#strategies for 3D array (5x5x5) with floats in [1,10]
array_dark = arrays(np.float32,([5,5,5]),elements=array_elements_dark,fill=st.nothing())

#==================================
#PROPERTY TESTING
#==================================

@given(im_stack=array_projections,
       rows_ROI = list_rows,
       columns_ROI = list_columns)
def test_cropping_same_lenght (im_stack,rows_ROI,columns_ROI):
    '''
    Test for the invariance of the number of images in
    the stack when images are cropped.
    It even asserts that the dimensions of the new images
    are equal or smaller than the initial images
    
    Given
    -----
    img_stack : ndarray
        3D array of float numbers representing a stack of images 5x5.
    rows_ROI,columns_ROI : list
        lists of two different sorted random integers representing the coordinates of the cropping region of interest (rows and columns)
'''
    rowmin=rows_ROI[0]
    rowmax=rows_ROI[1]
    colmin=columns_ROI[0]
    colmax=columns_ROI[1]


    im_stack_cropped=preprocess_and_correction.cropping(im_stack,rowmin,rowmax,colmin,colmax)

    assert im_stack_cropped.shape[0] == im_stack.shape[0]

    for i in range(len(im_stack_cropped.shape)):
        assert im_stack_cropped.shape[i] <= im_stack.shape[i]


#TO DO:check for the type of arrays for stack
@given(tomo_stack=array_projections,
       flat_stack=array_flat,
       dark_stack=array_dark)
def test_normalization_same_dimensions (tomo_stack,flat_stack,dark_stack):
    '''
    Test for the dimensions invariance of the stack of images
    after their normalization.
    
    Given
    -----
    tomo_stack : ndarray
        3D array of float numbers representing a stack of images with grey values between 1 and 250
    flat_stack : ndarray
        3D array of float numbers representing a stack of flat images with grey values between 250 and 255
    dark_stack : ndarray
        3D array of float numbers representing a stack of flat images with grey values between 1 and 10
    '''
    
    stack_norm = preprocess_and_correction.normalization(tomo_stack,dark_stack,flat_stack)


    for j in range(len(stack_norm.shape)):
            assert  stack_norm.shape[j] == tomo_stack.shape[j]



@given(tomo_stack=array_projections,
       flat_stack=array_flat,
       dark_stack=array_dark)
def test_normalization_max_value (tomo_stack,flat_stack,dark_stack):
    '''
    THe test asserts that the max px value of the normalized images
    is always equal or lower than the max px value of the inital images.
    
    Given
    -----
    tomo_stack : ndarray
        3D array of float numbers representing a stack of images with grey values between 1 and 250
    flat_stack : ndarray
        3D array of float numbers representing a stack of flat images with grey values between 250 and 255
    dark_stack : ndarray
        3D array of float numbers representing a stack of flat images with grey values between 1 and 10
    '''
    
    stack_norm = preprocess_and_correction.normalization(tomo_stack,dark_stack,flat_stack)

    list=[]
    for i in range(stack_norm.shape[0]):
        max_norm = np.max(stack_norm[i,:,:])
        max_no_norm = np.max(tomo_stack[i,:,:])
        h= max_norm <= max_no_norm
        list.append(h)

    res=all(l for l in list)
    assert res


@given(tomo_stack=array_projections,
       flat_stack=array_flat,
       dark_stack=array_dark)
def test_normalization_min_value (tomo_stack,flat_stack,dark_stack):
    '''
    The test asserts that the min px value of the normalized images
    is always equal or lower than the min px value of the inital images.
    
    Given
    -----
    tomo_stack : ndarray
        3D array of float numbers representing a stack of images with grey values between 1 and 250
    flat_stack : ndarray
        3D array of float numbers representing a stack of flat images with grey values between 250 and 255
    dark_stack : ndarray
        3D array of float numbers representing a stack of flat images with grey values between 1 and 10
    '''
    
    stack_norm = preprocess_and_correction.normalization(tomo_stack,dark_stack,flat_stack)

    list=[]
    for i in range(stack_norm.shape[0]):
        min_norm = np.min(stack_norm[i,:,:])
        min_no_norm = np.min(tomo_stack[i,:,:])
        h= min_norm <= min_no_norm
        list.append(h)

    res=all(l for l in list)
    assert res



@given(tomo_stack=array_projections,
       flat_stack=array_flat,
       dark_stack=array_dark)
def test_normalization_values_in_interval (tomo_stack,flat_stack,dark_stack):
    '''
    Test for the dimensions invariance of the stack of images
    after their normalization.
    It even even asserts that the max px value of the normalized images
    is always equal or lower than the max px value of the inital images.
    
    Given
    -----
    tomo_stack : ndarray
        3D array of float numbers representing a stack of images with grey values between 1 and 250
    flat_stack : ndarray
        3D array of float numbers representing a stack of flat images with grey values between 250 and 255
    dark_stack : ndarray
        3D array of float numbers representing a stack of flat images with grey values between 1 and 10
    '''
    
    stack_norm = preprocess_and_correction.normalization(tomo_stack,dark_stack,flat_stack)
    
    and_result = np.logical_and(stack_norm>=0,stack_norm<=1)
    all_result = np.all(and_result)
    assert all_result
    


@given(tomo_stack=array_projections,
       ans = st.text(alphabet= list('aAbBdD'), min_size=1,max_size=1),
       neighboors = st.integers(1,3))
#@settings(suppress_health_check=[HealthCheck.filter_too_much])
def test_out_filter_same_dimensions (tomo_stack,ans,neighboors):
    '''
    Test for the invariance of the dimensions of an image stack
    after the filtering from outliers of all images.
    The function to be tested "preprocess_and_correction.outliers_filter()"
    asks the user to type an accepted character on the keyboard in order
    to proceed with the corresponding filtering.
    Even this part of the function is tested.

    Given
    -----
    tomo_stack : ndarray
        3D array of float numbers representing a stack of images (10x10)
    ans : str
        string representing the answer of the user
    neighbooors : int
       random integer representing the neighborhood radius considered when the filtering is performed 
    '''
    
    with mock.patch('builtins.input',return_value=ans):
        tomo_stack_filt = preprocess_and_correction.outliers_filter(tomo_stack,neighboors)
        for j in range(len(tomo_stack.shape)):
            assert tomo_stack.shape[j] == tomo_stack_filt.shape[j]



@given(projection=array_2D,
       yROI_list=list_yROI)
@settings(deadline=None)
def test_find_offset_angle (projection,yROI_list):
    '''
    The test asserts that the tilt angle is between -90° and +90°.

    Given
    -----
    projection : ndarray
        2D array representing an image (10x10)
    yROI_list : list
        list of two different sorted random integers in [0,9] that represent the minimum and the maximun y coordinates
        of the image to consider for the analysis

    '''

    yROI=np.arange(yROI_list[0],yROI_list[1]+1,1) #+1 to include the last value

    assert abs(preprocess_and_correction.find_shift_and_tilt_angle(yROI,projection,projection)[-1]) <= 90.0



#==================================
#UNIT TESTING
#==================================

def test_cropping_good_coordinates():
    '''
    Test for the invariance of the number of images in
    the stack when images are cropped.
    The test asserts even that the dimensions of the cropped images correspond to the number
    of rows and the number of columns selected.
    '''
    np.random.seed(0)
    #random 3D array to represent en image stack
    img_array= np.random.rand(10,10,10)
    #coordinates for the ROI
    rowmin = 4
    rowmax = 8
    colmin = 4
    colmax = 8
    
    img_array_cropped=preprocess_and_correction.cropping(img_array,rowmin,rowmax,colmin,colmax)

    assert img_array_cropped.shape[0] == img_array.shape[0]
    assert img_array_cropped.shape[1] == 4
    assert img_array_cropped.shape[2] == 4

def test_cropping_bad_coordinates ():
    '''
    Test for the occurrence of error when incorrect ROI coordinates
    are given as input to the cropping function (preprocess_and_correction.cropping()),
    that crop all the images in a stack.
    '''
    np.random.seed(0)
    img_array= np.random.rand(10,10,10)
    rowmax =2
    rowmin = 5
    colmax = 3
    colmin = 6
    
    with pytest.raises(ValueError) as e:
        preprocess_and_correction.cropping(img_array,rowmin,rowmax,colmin,colmax)
    assert str(e.value) == 'rowmin and colmin must be less than rowmax and colmax rispectively'


def croping_ROI_as_the_image ():
    '''
    Test for the invariance of the dimensions of the 3D array containing
    2D images when images are cropped considering a ROI with the same size of the 2D images.
    '''
    np.random.seed(0)
    img_array= np.random.rand(10,10,10)
    rowmin=colmin=0
    rowmax=colmax=9

    assert preprocess_and_correction.cropping(img_array,rowmin,rowmax,colmin,colmax).shape == img_array.shape


def test_normalization_max_val():
    '''
    This test asserts that the max px value of the normalized images
    is always equal or lower than the max px value of the inital images.
    A set of 11 tomographic projections, contained in the path 'filepath',
    and a dark image and a flat image, contained rispectively in the paths 
    'darkpath' and 'flatpath', are used in the test.
    '''
    filepath='testing_images\\tomography\\projections'
    darkpath='testing_images\\tomography\\dark'
    flatpath='testing_images\\tomography\\flat'

    imlist=preparation_data.reader_gray_images(filepath)
    darklist=preparation_data.reader_gray_images(darkpath)
    flatlist=preparation_data.reader_gray_images(flatpath)

    imar=preparation_data.create_array(imlist,imlist)
    darkar=preparation_data.create_array(darklist,imlist)
    flatar=preparation_data.create_array(flatlist,imlist)

    im_norm = preprocess_and_correction.normalization(imar,darkar,flatar)

    list=[]
    for i in range(im_norm.shape[0]):
        max_norm = np.max(im_norm[i,:,:])
        max_no_norm = np.max(imar[i,:,:])
        h= max_norm <= max_no_norm
        list.append(h)

    res=all(l for l in list)
    assert res

def test_normalization_max_val():
    '''
    This test asserts that the min px value of the normalized images
    is always equal or lower than the min px value of the inital images.
    A set of 11 tomographic projections, contained in the path 'filepath',
    and a dark image and a flat image, contained rispectively in the paths 
    'darkpath' and 'flatpath', are used in the test.
    '''
    filepath='testing_images\\tomography\\projections'
    darkpath='testing_images\\tomography\\dark'
    flatpath='testing_images\\tomography\\flat'

    imlist=preparation_data.reader_gray_images(filepath)
    darklist=preparation_data.reader_gray_images(darkpath)
    flatlist=preparation_data.reader_gray_images(flatpath)

    imar=preparation_data.create_array(imlist,imlist)
    darkar=preparation_data.create_array(darklist,imlist)
    flatar=preparation_data.create_array(flatlist,imlist)

    im_norm = preprocess_and_correction.normalization(imar,darkar,flatar)

    list=[]
    for i in range(im_norm.shape[0]):
        min_norm = np.min(im_norm[i,:,:])
        min_no_norm = np.min(imar[i,:,:])
        h= min_norm <= min_no_norm
        list.append(h)

    res=all(l for l in list)
    assert res

def test_normalization_same_dimensions():
    '''
    This test asserts that the dimensions of the stack of normalized images
    is equal to the dimensions of the stack of inital images.
    A set of 11 tomographic projections, contained in the path 'filepath',
    and a dark image and a flat image, contained rispectively in the paths 
    'darkpath' and 'flatpath', are used in the test.
    '''
    filepath='testing_images\\tomography\\projections'
    darkpath='testing_images\\tomography\\dark'
    flatpath='testing_images\\tomography\\flat'

    imlist=preparation_data.reader_gray_images(filepath)
    darklist=preparation_data.reader_gray_images(darkpath)
    flatlist=preparation_data.reader_gray_images(flatpath)

    imar=preparation_data.create_array(imlist,imlist)
    darkar=preparation_data.create_array(darklist,imlist)
    flatar=preparation_data.create_array(flatlist,imlist)

    im_norm = preprocess_and_correction.normalization(imar,darkar,flatar)

    for i in range(len(im_norm.shape)):
        assert imar.shape[i] == im_norm.shape[i]


def test_norm_mean ():
    '''
    This test asserts that the mean of the normalized images is related to the mean
    of the initial images by the function used for the normalization: (I-mean(Imin))/(mean(Imax)-mean(Imin)).
    See the documentation in README.md file or the function preprocess_and_correction.normalization ()
    for more details.
    '''

    filepath='testing_images\\tomography\\projections'
    darkpath='testing_images\\tomography\\dark'
    flatpath='testing_images\\tomography\\flat'

    imlist=preparation_data.reader_gray_images(filepath)
    darklist=preparation_data.reader_gray_images(darkpath)
    flatlist=preparation_data.reader_gray_images(flatpath)

    imar=preparation_data.create_array(imlist,imlist)
    darkar=preparation_data.create_array(darklist,imlist)
    flatar=preparation_data.create_array(flatlist,imlist)

    norm_stack = preprocess_and_correction.normalization(imar,darkar,flatar)

    for i in range(norm_stack.shape[0]):
        res = (np.mean(imar[i-1,:,:])-np.mean(darkar[i-1,:,:]))/(np.mean(flatar[i-1,:,:])-np.mean(darkar[i-1,:,:]))
        assert math.isclose(np.mean(norm_stack[i-1,:,:]),res,rel_tol=1e-01)


def test_outliers_filter_bright_spot_image_b():
    '''
    Test for the filtering of bright outliers.
    A black image with few white spots is used to 
    create a 3D array with the same image repeated,
    given as input to the method that perform the filtering.
    The test asserts that, after the filtering, the only grey value 
    in the images is 0 (black colour).
    '''
    path='testing_images\\bright_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)

    with mock.patch('builtins.input',return_value='b'):
        im_stack_filt = preprocess_and_correction.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == np.min(im_stack_filt[i]) == 0.0

def test_outliers_filter_bright_spot_image_a():
    '''
    Test for the filtering of both bright and dark outliers.
    A black image with few white spots is used to 
    create a 3D array with the same image repeated,
    given as input to the method that perform the filtering.
    The test asserts that, after the filtering, the only grey value 
    in the images is 0 (black colour).
    '''
    path='testing_images\\bright_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)

    with mock.patch('builtins.input',return_value='a'):
        im_stack_filt = preprocess_and_correction.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == 0.0
            assert np.min(im_stack_filt[i]) == 0.0

def test_outliers_filter_bright_spot_image_d():
    '''
    Test for the filtering of dark outliers.
    A black image with few white spots is used to 
    create a 3D array with the same image repeated,
    given as input to the method that perform the filtering.
    The test asserts that, after the filtering, the images contain
    both grey value = 255 and grey value = 0 (both white and black colours).
    '''
    path='testing_images\\bright_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)
    with mock.patch('builtins.input',return_value='d'):
        im_stack_filt = preprocess_and_correction.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == 255.0 
            assert np.min(im_stack_filt[i]) == 0.0

def test_outliers_filter_dark_spot_image_d():
    '''
    Test for the filtering of dark outliers.
    A white image with few black spots is used to 
    create a 3D array with the same image repeated,
    given as input to the method that perform the filtering.
    The test asserts that, after the filtering, the only grey value 
    in the images is 255 (white colour).
    '''
    path='testing_images\\dark_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)

    with mock.patch('builtins.input',return_value='d'):
        im_stack_filt = preprocess_and_correction.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == 255.0
            assert np.min(im_stack_filt[i]) == 255.0

def test_outliers_filter_dark_spot_image_a():
    '''
    Test for the filtering of both dark and bright outliers.
    A white image with few black spots is used to 
    create a 3D array with the same image repeated,
    given as input to the method that perform the filtering.
    The test asserts that, after the filtering, the only grey value 
    in the images is 255 (white colour).
    '''
    path='testing_images\\dark_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)

    with mock.patch('builtins.input',return_value='a'):
        im_stack_filt = preprocess_and_correction.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == 255.0
            assert np.min(im_stack_filt[i]) == 255.0

def test_outliers_filter_dark_spot_image_b():
    '''
    Test for the filtering bright outliers.
    A white image with few black spots is used to 
    create a 3D array with the same image repeated,
    given as input to the method that perform the filtering.
    The test asserts that, after the filtering, the images contain
    both grey value = 255 and grey value = 0 (both white and black colours).
    '''
    path='C:\\Users\\Naomi\\correctionCOR\\testing_images\\dark_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)

    with mock.patch('builtins.input',return_value='b'):
        im_stack_filt = preprocess_and_correction.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == 255.0 
            assert np.min(im_stack_filt[i]) == 0.0


def test_outlier_filter_order ():
    '''
    This test assert that the order of application of the 
    outlier_filter for bright or dark outliers does not influence
    the result. In other words, the application of firstly the bright outlier
    filter and secondly of the dark outlier filter produces the same result
    of the inverse application.
    '''
    np.random.seed(0)
    stack = np.random.rand(10,10,10)

    with mock.patch('builtins.input',return_value='b'):
        stack_bd1 = preprocess_and_correction.outliers_filter(stack,3)
    with mock.patch('builtins.input',return_value='d'):
        stack_bd2 = preprocess_and_correction.outliers_filter(stack_bd1,3)

    with mock.patch('builtins.input',return_value='d'):
        stack_db1 = preprocess_and_correction.outliers_filter(stack,3)
    with mock.patch('builtins.input',return_value='b'):
        stack_db2 = preprocess_and_correction.outliers_filter(stack_db1,3)

    assert np.array_equal(stack_bd1,stack_db2) == True

def test_find_shift_and_theta_obj_shifted_and_tilted ():
    '''
    Test for the correctness of the computed values of the shift and
    the tilt angle of the axis of rotation with respect to the central vertical
    axis of the image.
    An image with a rectangle with inclination of 3° and shift of 54 px has been 
    created and used properly for the test (image represented by path1).
    '''
    path1='testing_images\\tomograf_incl.tiff'
    im=cv2.imread(path1,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)

    shift_known= 54
    theta_known = -3

    ymin=226
    ymax=844
    ystep=5
    y_of_ROIs= np.arange(ymin, ymax +1, ystep)

    m,q,shift,offset,middle_shift, theta=preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,im,im)

    assert np.isclose(offset,shift_known,rtol=1e-1,atol=1e-2)
    assert np.isclose(theta,theta_known,rtol=1e-1,atol=1e-2)

def test_find_shift_and_theta_obj_centr():
    '''
    Test for the correctness of the computed values of the shift and
    the tilt angle of the axis of rotation with respect to the central vertical
    axis of the image.
    An image with a rectangle with null inclination and shift has been created and used properly
    for the test (image represented by path1).
    '''
    path1='testing_images\\tomograf_centr.tiff'
    im=cv2.imread(path1,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)

    shift_known= 0
    theta_known = 0

    ymin=254
    ymax=845
    ystep=5
    y_of_ROIs= np.arange(ymin, ymax +1, ystep)

    m,q,shift,offset,middle_shift, theta=preprocess_and_correction.find_shift_and_tilt_angle(y_of_ROIs,im,im)

    assert np.isclose(offset,shift_known,rtol=1e-1,atol=1e-2)
    assert np.isclose(theta,theta_known,rtol=1e-1,atol=1e-2)

