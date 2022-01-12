import sys
sys.path.insert(0,".\\COR")
import pytest
from COR import preparation_data
from COR import preprocess_and_correction
import numpy as np
from unittest import mock
import cv2
from hypothesis import given
from hypothesis import settings
import hypothesis.strategies as st
from hypothesis.extra.numpy import arrays


#==================================
#PROPERTY TESTING
#==================================

@given(im_stack=arrays(dtype=float,shape=(np.random.randint(1,10),4,4),elements=st.floats(min_value=0,allow_nan=False, allow_infinity=False),fill=st.nothing()),
       rowmin=st.integers(0,3),
       rowmax=st.integers(0,3),
       colmin=st.integers(0,3),
       colmax=st.integers(0,3))
def test_cropping_same_lenght (im_stack,rowmin,rowmax,colmin,colmax):
    '''
    Test for the invariance of the number of images in
    the stack when images are cropped.
    It even asserts that the dimensions of the new images
    are equal or smaller than the initial images
    
    Given
    -----
    img_stack : ndarray
        3D array of float numbers representing a stack of images. The 2D images are (10px x 10px)
    rowmin,rowmax,colmin,colmax : int
        random integers representing the coordinates of the cropping region of interest
    '''
    if rowmax < rowmin or colmax < colmin:
        with pytest.raises(ValueError) as e:
            preprocess_and_correction.cropping(im_stack,rowmin,rowmax,colmin,colmax)
        assert str(e.value) == 'rowmin and colmin must be less than rowmax and colmax rispectively'

    else:
        im_stack_cropped=preprocess_and_correction.cropping(im_stack,rowmin,rowmax,colmin,colmax)

        assert im_stack_cropped.shape[0] == im_stack.shape[0]

        for i in range(len(im_stack_cropped.shape)):
            assert im_stack_cropped.shape[i] <= im_stack.shape[i]



@given(tomo_stack=arrays(dtype=float,shape=(np.random.randint(1,10),np.random.randint(1,5),np.random.randint(1,5)),elements=st.floats(0,25,allow_nan=False),fill=st.nothing()),
       flat_stack=arrays(dtype=float,shape=(np.random.randint(1,10),np.random.randint(1,5),np.random.randint(1,5)),elements=st.floats(23,25,allow_nan=False),fill=st.nothing()),
       dark_stack=arrays(dtype=float,shape=(np.random.randint(1,10),np.random.randint(1,5),np.random.randint(1,5)),elements=st.floats(0,2,allow_nan=False),fill=st.nothing()))
def test_norm_no_ROI (tomo_stack,flat_stack,dark_stack):
    '''
    Test for the dimensions invariance of the stack of images
    after their normalization.
    It even even asserts that the max px value of the normalized images
    is always equal or lower than the max px value of the inital images.
    
    Given
    -----
    tomo_stack : ndarray
        3D array of float numbers representing a stack of images with grey values between 0 and 25
    flat_stack : ndarray
        3D array of float numbers representing a stack of flat images with grey values between 23 and 25
    dark_stack : ndarray
        3D array of float numbers representing a stack of flat images with grey values between 0 and 2
    '''
    if tomo_stack.shape == flat_stack.shape and tomo_stack.shape == dark_stack.shape:
        stack_norm = preprocess_and_correction.normalization_no_ROI(tomo_stack,dark_stack,flat_stack)

        list=[]
        for i in range(stack_norm.shape[0]):
            max_norm = np.max(stack_norm[i,:,:])
            max_no_norm = np.max(tomo_stack[i,:,:])
            h= max_norm <= max_no_norm
            list.append(h)

        res=all(l for l in list)
        assert res

        for j in range(len(stack_norm.shape)):
            assert tomo_stack.shape[j] == stack_norm.shape[j]
        
    else:
        with pytest.raises(ValueError) as err:
            preprocess_and_correction.normalization_no_ROI(tomo_stack,dark_stack,flat_stack)
        assert str(err.value) == 'the stack of images (tomographic projections,flat images and dark images) must have the same dimensions'


@given(tomo_stack=arrays(dtype=float,shape=(np.random.randint(1,10),5,5),elements=st.floats(0,25,allow_nan=False),fill=st.nothing()),
       flat_stack=arrays(dtype=float,shape=(np.random.randint(1,10),5,5),elements=st.floats(23,25,allow_nan=False),fill=st.nothing()),
       dark_stack=arrays(dtype=float,shape=(np.random.randint(1,10),5,5),elements=st.floats(0,2,allow_nan=False),fill=st.nothing()),
       rowmin=st.integers(0,4),
       rowmax=st.integers(0,4),
       colmin=st.integers(0,4),
       colmax=st.integers(0,4))
def test_norm_ROI (tomo_stack,flat_stack,dark_stack,rowmin,rowmax,colmin,colmax):
    '''
    Test for the dimensions invariance of the cropped stack of images
    after their normalization, condsidering a cropping region of interest.
    It even even asserts that the max px value of the normalized images
    is always equal or lower than the max px value of the inital images.

    Given
    -----
    tomo_stack : ndarray
        3D array of float numbers representing a stack of images (5x5) with grey values between 0 and 25
    flat_stack : ndarray
        3D array of float numbers representing a stack of flat images (5x5) with grey values between 23 and 25
    dark_stack : ndarray
        3D array of float numbers representing a stack of flat images (5x5) with grey values between 0 and 2
    rowmin,rowmax,colmin,colmax : int
        random integers representing the coordinates of the cropping region of interest
    '''
    if tomo_stack.shape == flat_stack.shape and tomo_stack.shape == dark_stack.shape:

        if rowmin <= rowmax and colmin <= colmax:
            stack_norm = preprocess_and_correction.normalization_no_ROI(tomo_stack,dark_stack,flat_stack)

            list=[]
            new_dim = (tomo_stack.shape[0],rowmax-rowmin,colmax-colmin)

            for i in range(stack_norm.shape[0]):
                max_norm = np.max(stack_norm[i,:,:])
                max_no_norm = np.max(tomo_stack[i,rowmin:rowmax,colmin:colmax])
                h= max_norm <= max_no_norm
                list.append(h)
                res=all(l for l in list)
            assert res
            
            for j in range(len(stack_norm.shape)):
                assert new_dim[j] <= stack_norm.shape[j]

        else:
            with pytest.raises(ValueError) as err:
                preprocess_and_correction.normalization_with_ROI(tomo_stack,dark_stack,flat_stack,rowmin,rowmax,colmin,colmax)
            assert str(err.value) == 'rowmin and colmin must be less than rowmax and colmax rispectively'

    else:
        with pytest.raises(ValueError) as e:
            preprocess_and_correction.normalization_with_ROI(tomo_stack,dark_stack,flat_stack,rowmin,rowmax,colmin,colmax)
        assert str(e.value) == 'the stack of images (tomographic projections,flat images and dark images) must have the same dimensions'


@given(tomo_stack=arrays(dtype=float,shape=(np.random.randint(1,10),4,4),elements=st.floats(0,255,allow_nan=False),fill=st.nothing()),
       ans = st.characters(),
       neighboors = st.integers(1,10))
def test_out_filter (tomo_stack,ans,neighboors):
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
    ans_acc = ['b','B','d','D','a','A']

    if any(ans == i for i in ans_acc):
        with mock.patch('builtins.input',return_value=ans):
            tomo_stack_filt = preprocess_and_correction.outliers_filter(tomo_stack,neighboors)
            for j in range(len(tomo_stack.shape)):
                assert tomo_stack.shape[j] == tomo_stack_filt.shape[j]

    else:
        with mock.patch('builtins.input',return_value=ans):
            with pytest.raises(IOError) as err:
                preprocess_and_correction.outliers_filter(tomo_stack,neighboors)
            assert str(err.value) == 'Input not valid.'


@given(projection=arrays(dtype=float,shape=(10,10),elements=st.floats(1,255,allow_nan=False),fill=st.nothing()),
       ymin=st.integers(0,9),
       ymax=st.integers(0,9))
@settings(deadline=None)
def test_find_offset_angle (projection,ymin,ymax):
    '''
    Test for the type of the returned values of the function
    that finds the shift and the tilt angle of the rotation axis
    (preprocess_and_correction.find_shift_and_tilt_angle()).
    It even asserts that the tilt angle is between -90° and +90°.

    Given
    -----
    projection : ndarray
        2D array representing an image (10x10)
    ymin,ymax : int
        random integers that represent the minimum and the maximun y coordinates
        of the image to consider for the analysis

    '''
    yROI=np.arange(min(ymin,ymax),max(ymin,ymax)+1,1) #+1 to include the last value

    if ymin == ymax:
        with pytest.raises(ValueError) as err:
            preprocess_and_correction.find_shift_and_tilt_angle(yROI,projection,projection)
        assert str(err.value) == 'ROI height must be greater than zero'

    else:
        m,q,shift,offset,middle_shift,theta= preprocess_and_correction.find_shift_and_tilt_angle(yROI,projection,projection)
        assert type(offset) == type(theta) == type(m) == type(q) == np.float64
        assert type(middle_shift) == np.int32
        assert type(shift) == np.ndarray
        assert theta <= 90.0 and theta >= -90.0



#==================================
#UNIT TESTING
#==================================

def test_cropping_good_coordinates():
    '''
    Test for the invariance of the number of images in
    the stack when images are cropped.
    Acceptable coordinates for the cropping ROI (rowmin <= rowmax and colmin <= colmax)
    are randomly generated.
    It even asserts that the dimensions of the new images
    are equal or smaller than the initial images
    '''
    #random 3D array to represent en image stack
    img_array= np.random.rand(10,20,20)
    #coordinates for the ROI
    rowmin = np.random.randint(0,20)
    rowmax = np.random.randint(rowmin,20)
    colmin = np.random.randint(0,20)
    colmax = np.random.randint(colmin,20)
    
    img_array_cropped=preprocess_and_correction.cropping(img_array,rowmin,rowmax,colmin,colmax)

    assert img_array_cropped.shape[0] == img_array.shape[0]

    for i in range(len(img_array_cropped.shape)):
        assert img_array_cropped.shape[i] <= img_array.shape[i]

def test_cropping_bad_coordinates ():
    '''
    Test for the occurrence of error when incorrect ROI coordinates
    are given as input to the cropping function (preprocess_and_correction.cropping()),
    that crop all the images in a stack.
    '''
    img_array= np.random.rand(10,20,20)
    rowmax = np.random.randint(0,20)
    rowmin = np.random.randint(rowmax,20)
    colmax = np.random.randint(0,20)
    colmin = np.random.randint(colmax,20)
    
    with pytest.raises(ValueError) as e:
        preprocess_and_correction.cropping(img_array,rowmin,rowmax,colmin,colmax)
    assert str(e.value) == 'rowmin and colmin must be less than rowmax and colmax rispectively'

def test_normalization_no_ROI_max_val():
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

    im_norm = preprocess_and_correction.normalization_no_ROI(imar,darkar,flatar)

    list=[]
    for i in range(im_norm.shape[0]):
        max_norm = np.max(im_norm[i,:,:])
        max_no_norm = np.max(imar[i,:,:])
        h= max_norm <= max_no_norm
        list.append(h)

    res=all(l for l in list)
    assert res

def test_normalization_no_ROI_same_dimensions():
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

    im_norm = preprocess_and_correction.normalization_no_ROI(imar,darkar,flatar)

    for i in range(len(im_norm.shape)):
        assert imar.shape[i] == im_norm.shape[i]

def test_normalization_ROI_max_val():
    '''
    This test asserts that the max px value of the normalized images
    is always equal or lower than the max px value of the inital images.
    The normalization is performed on cropped images.
    The coordinates of the crop ROI are randomly generated.
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

    rowmin = np.random.randint(0,999)
    rowmax = np.random.randint(rowmin,999)
    colmin = np.random.randint(0,1099)
    colmax = np.random.randint(colmin,1099)

    im_norm = preprocess_and_correction.normalization_with_ROI(imar,darkar,flatar,rowmin,rowmax,colmin,colmax)

    list=[]
    for i in range(im_norm.shape[0]):
        max_norm = np.max(im_norm[i,:,:])
        max_no_norm = np.max(imar[i,rowmin:rowmax,colmin:colmax])
        h= max_norm <= max_no_norm
        list.append(h)

    res=all(l for l in list)
    assert res

def test_normalization_ROI_same_dim ():
    '''
    This test asserts that the dimensions of the stack of  normalized cropped images
    is equal to the dimensions of the stack of the cropped inital images.
    The coordinates of the crop ROI are randomly generated.
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

    rowmin = np.random.randint(0,999)
    rowmax = np.random.randint(rowmin,999)
    colmin = np.random.randint(0,1099)
    colmax = np.random.randint(colmin,1099)

    new_dim = (imar.shape[0],rowmax-rowmin,colmax-colmin)

    im_norm = preprocess_and_correction.normalization_with_ROI(imar,darkar,flatar,rowmin,rowmax,colmin,colmax)
    
    for i in range(len(im_norm.shape)):
        assert im_norm.shape[i] == new_dim[i]

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
            assert np.max(im_stack_filt[i]) == np.min(im_stack_filt[i]) == 0.0

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
            assert np.max(im_stack_filt[i]) == np.min(im_stack_filt[i]) == 255.0

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
            assert np.max(im_stack_filt[i]) == np.min(im_stack_filt[i]) == 255.0

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

