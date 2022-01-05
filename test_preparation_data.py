import pytest
import preparation_data
import numpy as np
import os
from hypothesis import given
import hypothesis.strategies as st
from hypothesis.extra.numpy import arrays



#============================================
#PROPERTY TESTING
#============================================

blacklist = [".", "<", ">", ":", '"', "/", "|", "?", "*"]
@given(filepath=st.text(st.characters(blacklist_characters=blacklist,min_codepoint=32,max_codepoint=126),min_size=1,max_size=64)) #codepoints include basic Latin from https://en.wikipedia.org/wiki/List_of_Unicode_characters
def test_reader_gray_images_random_filepath (filepath):
    '''
    Test for asserting that the method preparation_data.reader_gray_images(),
    when the filepath given as input exists and contains .tiff files,
    returns a non empty list

    Given
    -----
    filepath : str
        a string of min 1 character and max 64 characters defining the filepath eventually 
        containing .tiff files
    '''
    if os.path.isdir(filepath):
        if (not any(fname.endswith('.tiff')) for fname in os.listdir(filepath)):
            with pytest.raises(ImportError) as er:
                preparation_data.reader_gray_images(filepath)
            assert str(er.value) == 'directory {0} does not contain any .tiff file'.format(filepath)
        else:
            assert len(preparation_data.reader_gray_images(filepath)) > 0
    else:
        with pytest.raises(ImportError) as e:
            preparation_data.reader_gray_images(filepath)
        assert str(e.value) == 'directory {0} does not exist'.format(filepath)


@given(list1=st.lists(arrays(dtype=float,shape=(np.random.randint(1,10),np.random.randint(1,10)),elements=st.floats(min_value=0,allow_nan=False, allow_infinity=False),fill=st.nothing()),min_size=1),
       list2=st.lists(arrays(dtype=float,shape=(np.random.randint(1,10),np.random.randint(1,10)),elements=st.floats(min_value=0,allow_nan=False, allow_infinity=False),fill=st.nothing()),min_size=1))
def test_create_array_propr(list1,list2):
    '''
    Test that asserts that, when creating the 3D array representing
    the stack of images from a list containing one 
    or more images, considering a reference list,
    the first dimension of the array is equal to the lenght 
    of the reference list and the other 2 dimensions of the array are equal to
    the dimensions of the images in the list (equal to the dimensions of the
    images in the reference list).
    The method to be tested, preparation_data.create_array(), needs a second
    list of elements as reference, and the number of these elements 
    will be equal to the first dimension of the final array.

    Given
    -----
    list1, list2 : list
        lists of arrays of random floats representing list of images. 
    '''
    if list1[0].shape == list2[0].shape:

        if len(list1) != 1 or len(list1) != len(list2):
            with pytest.raises(ValueError) as er:
                preparation_data.create_array(list1,list2)
            assert str(er.value) == '{0} should contain or 1 image or an amount of images equal to the num of tomographic projections'.format(list1)
        
        else:
            assert preparation_data.create_array(list1,list2).shape[0] == len(list2)
            
            for i in range(2):
                assert preparation_data.create_array(list1,list2).shape[i+1] == list2[0].shape[i]
    
    else:
        with pytest.raises(ValueError) as e:
            preparation_data.create_array(list1,list2)
        assert str(e.value) == '{0} should contain images with the same dimensions of tomographic projections'.format(list1)


@given(angle=st.integers(min_value=0,max_value=360),
       array=arrays(dtype=float,shape=(np.random.randint(1,10),np.random.randint(1,10),np.random.randint(1,10)),elements=st.floats(min_value=0,allow_nan=False, allow_infinity=False),fill=st.nothing()))
def test_proj_0_180 (angle,array):
    '''
    Test for the inveriance of the dimensions of the 2D images returned
    from the function preparation_data.projection_0_180() that select the
    image acquired at the angle 0° and the one acquired at 180° from 
    the stack of images obtained from a tomography with last angle equal
    to 180° or 360°.

    Given
    -----
    angle : int
        random integer between 0 and 360 that represents the last angle of tomographic acquisition
    array : ndarray
       3D array of floats representing a stack of images
    '''
    if angle == 180 or angle == 360:
        for i in range(2): #loop over outputs
            for j in range (2): #loop over dimensions
                assert array.shape[j+1] == preparation_data.projection_0_180(angle,array)[i].shape[j]
    else:
        with pytest.raises(ValueError) as e:
            preparation_data.projection_0_180(angle,array)
        assert str(e.value) == 'the maximum angle for the tomography should be or 180 or 360 degrees'

    




#=============================================
#UNIT TESTING
#=============================================

def test_reader_gray_image_wrong_filepath ():
    filepath = 'not\\existing\\path'
    with pytest.raises(ImportError) as e:
        preparation_data.reader_gray_images(filepath)
    assert str(e.value) == 'directory {0} does not exist'.format(filepath)

def test_reader_gray_image_good_data ():
    filepath = 'C:\\Users\\Naomi\\correctionCOR\\images\\Flat_Darth_Vader'
    im_list = preparation_data.reader_gray_images(filepath)
    assert len(im_list) == 1

def test_create_array ():
    test_array = np.random.rand(3,2,2)
    test_ref_list = test_array.tolist()
    fin_array = preparation_data.create_array(test_ref_list,test_ref_list)
    assert fin_array.shape == test_array.shape

def test_create_array_one_img ():
    test_array = np.random.rand(3,2,2)
    test_ref_list = test_array.tolist()
    test_list = np.random.rand(1,2,2).tolist()
    fin_array = preparation_data.create_array(test_list,test_ref_list)
    assert fin_array.shape == test_array.shape

def test_create_array_few_img ():
    test_array = np.random.rand(3,2,2)
    test_ref_list = test_array.tolist()
    test_list = np.random.rand(2,2,2).tolist()
    with pytest.raises(ValueError) as e:
        preparation_data.create_array(test_list,test_ref_list)
    assert str(e.value) == '{0} should contain or 1 image or an amount of images equal to the num of tomographic projections'.format(test_list)

def test_create_array_wrong_list ():
    test_ref_list = np.random.rand(3,2,5).tolist()
    test_list = np.random.rand(3,4,2).tolist()
    ref_dim = np.array(test_ref_list[0]).shape
    test_dim = np.array(test_list[0]).shape
    with pytest.raises(ValueError) as e:
        preparation_data.create_array(test_list,test_ref_list)
    assert str(e.value) == '{0} should contain images with the same dimensions of tomographic projections'.format(test_list)

def test_projection_0_180_correct_values ():
    array=np.random.rand(4,2,2)
    array_corr=np.where(np.isnan(array),0,array)
    arr_360_0,arr_360_180=preparation_data.projection_0_180(360,array_corr)
    arr_180_0,arr_180_180=preparation_data.projection_0_180(180,array_corr)
    assert np.array_equiv(array_corr[0],arr_360_0)
    assert np.array_equiv(array_corr[1],arr_360_180)
    assert np.array_equiv(array_corr[0],arr_180_0)
    assert np.array_equiv(array_corr[3],arr_180_180)

