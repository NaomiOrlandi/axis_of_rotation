import pytest
import preprocessing_and_COR
import preparation_data
import numpy as np
from unittest import mock
import cv2
from hypothesis import given
import hypothesis.strategies as st
from hypothesis.extra.numpy import arrays


#==================================
#PROPERTY TESTING
#==================================

@given(im_stack=arrays(dtype=float,shape=(np.random.randint(1,10),np.random.randint(1,10),np.random.randint(1,10)),elements=st.floats(min_value=0,allow_nan=False, allow_infinity=False),fill=st.nothing()),
       rowmin=st.integers(0,30),
       rowmax=st.integers(0,30),
       colmin=st.integers(0,30),
       colmax=st.integers(0,30))
def test_cropping_same_lenght (im_stack,rowmin,rowmax,colmin,colmax):
    if rowmax < rowmin or colmax < colmin:
        with pytest.raises(ValueError) as e:
            preprocessing_and_COR.cropping(im_stack,rowmin,rowmax,colmin,colmax)
        assert str(e.value) == 'rowmin and colmin must be less than rowmax and colmax rispectively'
    else:
        im_stack_cropped=preprocessing_and_COR.cropping(im_stack,rowmin,rowmax,colmin,colmax)
        assert im_stack_cropped.shape[0] == im_stack.shape[0]
        for i in range(len(im_stack_cropped.shape)):
            assert im_stack_cropped.shape[i] <= im_stack.shape[i]



@given(tomo_stack=arrays(dtype=float,shape=(np.random.randint(1,10),np.random.randint(1,10),np.random.randint(1,10)),elements=st.floats(0,255,allow_nan=False),fill=st.nothing()),
       flat_stack=arrays(dtype=float,shape=(np.random.randint(1,10),np.random.randint(1,10),np.random.randint(1,10)),elements=st.floats(245,255,allow_nan=False),fill=st.nothing()),
       dark_stack=arrays(dtype=float,shape=(np.random.randint(1,10),np.random.randint(1,10),np.random.randint(1,10)),elements=st.floats(0,10,allow_nan=False),fill=st.nothing()))
def test_norm_no_ROI (tomo_stack,flat_stack,dark_stack):
    if tomo_stack.shape == flat_stack.shape == dark_stack.shape:
        stack_norm = preprocessing_and_COR.normalization_no_ROI(tomo_stack,dark_stack,flat_stack)
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
            preprocessing_and_COR.normalization_no_ROI(tomo_stack,dark_stack,flat_stack)
        assert str(err.value) == 'the stack of images (tomographic projections,flat images and dark images) must have the same dimensions'


    





#==================================
#UNIT TESTING
#==================================

def test_cropping_good_coordinates():
    img_array= np.random.rand(10,20,20)
    rowmin = np.random.randint(0,20)
    rowmax = np.random.randint(rowmin,20)
    colmin = np.random.randint(0,20)
    colmax = np.random.randint(colmin,20)
    img_array_cropped=preprocessing_and_COR.cropping(img_array,rowmin,rowmax,colmin,colmax)
    for i in range(len(img_array_cropped.shape)):
        assert img_array_cropped.shape[i] <= img_array.shape[i]

def test_cropping_bad_coordinates ():

    img_array= np.random.rand(10,20,20)
    rowmax = np.random.randint(0,20)
    rowmin = np.random.randint(rowmax,20)
    colmax = np.random.randint(0,20)
    colmin = np.random.randint(colmax,20)
    
    with pytest.raises(ValueError) as e:
        img_array_crp=preprocessing_and_COR.cropping(img_array,rowmin,rowmax,colmin,colmax)
    assert str(e.value) == 'rowmin and colmin must be less than rowmax and colmax rispectively'

def test_normalization_no_ROI_max_val():
    filepath='C:\\Users\\Naomi\\correctionCOR\\Tomo_10'
    darkpath='C:\\Users\\Naomi\\correctionCOR\\images\\Dark_Darth_Vader'
    flatpath='C:\\Users\\Naomi\\correctionCOR\\images\\Flat_Darth_Vader'

    imlist=preparation_data.reader_gray_images(filepath)
    darklist=preparation_data.reader_gray_images(darkpath)
    flatlist=preparation_data.reader_gray_images(flatpath)

    imar=preparation_data.create_array(imlist,imlist)
    darkar=preparation_data.create_array(darklist,imlist)
    flatar=preparation_data.create_array(flatlist,imlist)
    im_norm = preprocessing_and_COR.normalization_no_ROI(imar,darkar,flatar)
    list=[]
    for i in range(im_norm.shape[0]):
        max_norm = np.max(im_norm[i,:,:])
        max_no_norm = np.max(imar[i,:,:])
        h= max_norm <= max_no_norm
        list.append(h)
    res=all(l for l in list)
    assert res

def test_normalization_no_ROI_same_dimensions():
    filepath='C:\\Users\\Naomi\\correctionCOR\\Tomo_10'
    darkpath='C:\\Users\\Naomi\\correctionCOR\\images\\Dark_Darth_Vader'
    flatpath='C:\\Users\\Naomi\\correctionCOR\\images\\Flat_Darth_Vader'

    imlist=preparation_data.reader_gray_images(filepath)
    darklist=preparation_data.reader_gray_images(darkpath)
    flatlist=preparation_data.reader_gray_images(flatpath)

    imar=preparation_data.create_array(imlist,imlist)
    darkar=preparation_data.create_array(darklist,imlist)
    flatar=preparation_data.create_array(flatlist,imlist)
    im_norm = preprocessing_and_COR.normalization_no_ROI(imar,darkar,flatar)
    for i in range(len(im_norm.shape)):
        assert imar.shape[i] == im_norm.shape[i]

def test_normalization_ROI_max_val():
    filepath='C:\\Users\\Naomi\\correctionCOR\\Tomo_10'
    darkpath='C:\\Users\\Naomi\\correctionCOR\\images\\Dark_Darth_Vader'
    flatpath='C:\\Users\\Naomi\\correctionCOR\\images\\Flat_Darth_Vader'

    imlist=preparation_data.reader_gray_images(filepath)
    darklist=preparation_data.reader_gray_images(darkpath)
    flatlist=preparation_data.reader_gray_images(flatpath)

    imar=preparation_data.create_array(imlist,imlist)
    darkar=preparation_data.create_array(darklist,imlist)
    flatar=preparation_data.create_array(flatlist,imlist)

    rowmin = np.random.randint(0,2080)
    rowmax = np.random.randint(rowmin,2080)
    colmin = np.random.randint(0,3096)
    colmax = np.random.randint(colmin,3096)

    im_norm = preprocessing_and_COR.normalization_with_ROI(imar,darkar,flatar,rowmin,rowmax,colmin,colmax)
    list=[]
    for i in range(im_norm.shape[0]):
        max_norm = np.max(im_norm[i,:,:])
        max_no_norm = np.max(imar[i,:,:])
        h= max_norm <= max_no_norm
        list.append(h)
    res=all(l for l in list)
    assert res

def test_normalization_ROI_same_dim ():
    filepath='C:\\Users\\Naomi\\correctionCOR\\Tomo_10'
    darkpath='C:\\Users\\Naomi\\correctionCOR\\images\\Dark_Darth_Vader'
    flatpath='C:\\Users\\Naomi\\correctionCOR\\images\\Flat_Darth_Vader'

    imlist=preparation_data.reader_gray_images(filepath)
    darklist=preparation_data.reader_gray_images(darkpath)
    flatlist=preparation_data.reader_gray_images(flatpath)

    imar=preparation_data.create_array(imlist,imlist)
    darkar=preparation_data.create_array(darklist,imlist)
    flatar=preparation_data.create_array(flatlist,imlist)

    rowmin = np.random.randint(0,2080)
    rowmax = np.random.randint(rowmin,2080)
    colmin = np.random.randint(0,3096)
    colmax = np.random.randint(colmin,3096)

    new_dim = (imar.shape[0],rowmax-rowmin,colmax-colmin)

    im_norm = preprocessing_and_COR.normalization_with_ROI(imar,darkar,flatar,rowmin,rowmax,colmin,colmax)
    
    for i in range(len(im_norm.shape)):
        assert im_norm.shape[i] == new_dim[i]

def test_outliers_filter_bright_spot_image_b():
    path='C:\\Users\\Naomi\\correctionCOR\\bright_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)

    with mock.patch('builtins.input',return_value='b'):
        im_stack_filt = preprocessing_and_COR.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == np.min(im_stack_filt[i]) == 0.0

def test_outliers_filter_bright_spot_image_a():
    path='C:\\Users\\Naomi\\correctionCOR\\bright_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)

    with mock.patch('builtins.input',return_value='a'):
        im_stack_filt = preprocessing_and_COR.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == np.min(im_stack_filt[i]) == 0.0

def test_outliers_filter_bright_spot_image_d():
    path='C:\\Users\\Naomi\\correctionCOR\\bright_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)
    with mock.patch('builtins.input',return_value='d'):
        im_stack_filt = preprocessing_and_COR.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == 255.0 
            assert np.min(im_stack_filt[i]) == 0.0

def test_outliers_filter_dark_spot_image_d():
    path='C:\\Users\\Naomi\\correctionCOR\\dark_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)

    with mock.patch('builtins.input',return_value='d'):
        im_stack_filt = preprocessing_and_COR.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == np.min(im_stack_filt[i]) == 255.0

def test_outliers_filter_dark_spot_image_a():
    path='C:\\Users\\Naomi\\correctionCOR\\dark_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)

    with mock.patch('builtins.input',return_value='a'):
        im_stack_filt = preprocessing_and_COR.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == np.min(im_stack_filt[i]) == 255.0

def test_outliers_filter_dark_spot_image_b():
    path='C:\\Users\\Naomi\\correctionCOR\\dark_spot.tiff'
    im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    im_stack=np.full((3,506,900),im)

    with mock.patch('builtins.input',return_value='b'):
        im_stack_filt = preprocessing_and_COR.outliers_filter(im_stack,5)
        
        for i in range(3):
            assert np.max(im_stack_filt[i]) == 255.0 
            assert np.min(im_stack_filt[i]) == 0.0
'''
def test_find_shift_and_theta_obj_shifted_and_tilted ():
    path1='C:\\NAOMI_DATI\\UNIBO\\Magistrale\\Tesi\\Tomo_nota\\prova\\tomograf.tiff'
    im=cv2.imread(path1,cv2.IMREAD_GRAYSCALE)
    im=im.astype(np.float32)
    shift_known= 54
    theta_known = -3
    ymin=226
    ymax=844
    ystep=5
    y_ot_ROIs= np.arange(ymin, ymax +1, ystep)
    shift,theta=preprocessing_and_COR.find_shift_and_tilt_angle(y_ot_ROIs,im,im)
    assert np.isclose(shift,shift_known,rtol=1e-1,atol=1e-2)
    assert np.isclose(theta,theta_known,rtol=1e-1,atol=1e-2)

'''


