import pytest
import COR.preparation_data as preparation_data
import numpy as np
import os
from hypothesis import given
import hypothesis.strategies as st
from hypothesis.extra.numpy import arrays,array_shapes


np.random.seed(0)

#angles used in test_proj_0_180_dimensions() and test_projection_0_180_correct_angles()
angle1=180
angle2=360
#stategy for the shape of a 3D array
shape_3D = array_shapes(min_dims=3,max_dims=3,min_side=1,max_side=10)
#strategy for the elements of arrays (floats)
array_elements = st.floats(min_value=0,allow_nan=False, allow_infinity=False)
#strategy for a 3D array
array_3D = arrays(float,shape_3D,elements=array_elements,fill=st.nothing())
#strategy for a 2D array (5x5)
array_in_list = arrays(float,(5,5),elements=array_elements,fill=st.nothing())




#============================================
#PROPERTY TESTING
#============================================

@given(list_few_elements=st.lists(array_in_list,min_size=2),
       list_one_element=st.lists(array_in_list,min_size=1,max_size=1))
def test_create_array_shape(list_few_elements,list_one_element):
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
    list_few_elements, list_one_element : list
        lists of arrays of random floats representing list of images. 
    '''
    
    
    assert preparation_data.create_array(list_few_elements,list_few_elements).shape == tuple([len(list_few_elements),list_few_elements[0].shape[0],list_few_elements[0].shape[1]])
    assert preparation_data.create_array(list_one_element,list_few_elements).shape == tuple([len(list_few_elements),list_few_elements[0].shape[0],list_few_elements[0].shape[1]])
    


@given(array=array_3D)
def test_proj_0_180_dimensions (array):
    '''
    Test for the invariance of the dimensions of the 2D images returned
    from the function preparation_data.projection_0_180() that select the
    image acquired at the angle 0° and the one acquired at 180° from 
    the stack of images obtained from a tomography with last angle equal
    to 180° or 360°.

    Given
    -----
    array : ndarray
       3D array of floats representing a stack of images
    '''


    for i in range(2):
        for j in range(2):
            assert preparation_data.projection_0_180(angle1,array)[i].shape[j] == array.shape[j+1]
            assert preparation_data.projection_0_180(angle2,array)[i].shape[j] == array.shape[j+1]
    





#=============================================
#UNIT TESTING
#=============================================

def test_reader_gray_image_wrong_filepath ():
    '''
    Test for the occurrence of ImportError when the input 
    filepath to the function for reading .tiff images, 
    preparation_data.reader_gray_images(), does not exist.
    '''
    filepath = 'not\\existing\\path'
    with pytest.raises(OSError) as e:
        preparation_data.reader_gray_images(filepath)
    assert str(e.value) == 'directory {0} does not exist'.format(filepath)


def test_reader_gray_image_good_data ():
    '''
    Test for preparation_data.reader_gray_images() function, when the input
    filepath contains one images.
    It asserts that the list created has unit lenght
    '''
    filepath = 'testing_images\\tomography\\dark'
    im_list = preparation_data.reader_gray_images(filepath)
    assert len(im_list) == 1

def test_create_array ():
    '''
    Test for the function preparation_data.create_array(), which creates 
    3D array from a list of 2D arrays
    (3D array from a list containing grey scaled images),considering
    the lenght of a reference list of images.
    The test asserts that the shape of the final array from a list 
    with same lenght to the reference list is equal to the 
    shape of the reference list transformed in 3D array
    '''
    test_array = np.random.rand(3,2,2)
    test_ref_list = test_array.tolist()
    fin_array = preparation_data.create_array(test_ref_list,test_ref_list)
    assert fin_array.shape == test_array.shape



def test_create_array_one_img ():
    '''
    Test for the preparation_data.create_array() function when the initial
    list contains one element, while the reference list contains 3 elements.
    The test asserts that the shape of the 3D array returned from the initial list
    is equal to the shape of ref list transformed to a 3D array
    '''
    test_array = np.random.rand(3,2,2)
    test_ref_list = test_array.tolist()
    test_list = np.random.rand(1,2,2).tolist()
    fin_array = preparation_data.create_array(test_list,test_ref_list)
    assert fin_array.shape == test_array.shape



def test_create_array_few_img ():
    '''
    Test for the preparation_data.create_array() function when the initial
    list contains few element, more than one and less than
    the ones contained in the reference list.
    The test controll the raise of ValueError
    '''
    test_array = np.random.rand(3,2,2)
    test_ref_list = test_array.tolist()
    test_list = np.random.rand(2,2,2).tolist()
    with pytest.raises(ValueError) as e:
        preparation_data.create_array(test_list,test_ref_list)
    assert str(e.value) == '{0} should contain or 1 image or an amount of images equal to the num of tomographic projections'.format(test_list)



def test_create_array_wrong_list ():
    '''
    Test for preparation_data.create_array() function when the dimensions of 
    the 2D arrays contained in the list to be transformed in 3D array
    are different from the dimensions of the 2D arrays contained in the 
    reference list.
    It asserts the raise of ValueError with the correct message.
    '''
    test_ref_list = np.random.rand(3,2,5).tolist()
    test_list = np.random.rand(3,4,2).tolist()
    with pytest.raises(ValueError) as e:
        preparation_data.create_array(test_list,test_ref_list)
    assert str(e.value) == '{0} should contain images with the same dimensions of tomographic projections'.format(test_list)




def test_projection_0_180_correct_angles ():
    '''
    Test for preparation_data.projection_0_180() function, that from a stack
    of images (3D array) returns the tomogrphic image acquired at 0° (the first image)
    and the one acquired at 180° (the image at the end or in the middle of the stack,
    depending if the last angle of acquisition is 180° or 360°)
    The test assert that the two images selected in the stack are corrected.
    In this test the angles considered are 180 (angle1 )and 360 (angle2).
    '''
    array=np.random.rand(5,2,2)
    array_corr=np.where(np.isnan(array),0,array)
    arr_360_0,arr_360_180=preparation_data.projection_0_180(angle2,array_corr)
    arr_180_0,arr_180_180=preparation_data.projection_0_180(angle1,array_corr)
    assert np.array_equiv(array_corr[0],arr_360_0)
    assert np.array_equiv(array_corr[2],arr_360_180)
    assert np.array_equiv(array_corr[0],arr_180_0)
    assert np.array_equiv(array_corr[4],arr_180_180)

def test_projection_0_180_wrong_angle ():
    '''
    Test for preparation_data.projection_0_180() function, that from a stack
    of images (3D array) returns the tomogrphic image acquired at 0° (the first image)
    and the one acquired at 180° (the image at the end or in the middle of the stack,
    depending if the last angle of acquisition is 180° or 360°)
    In this test an angle different from 180 or 360 degrees is considered.
    Hence the raise of ValueError with the corresponding message is asserted.
    '''
    array=np.random.rand(5,2,2)
    array_corr=np.where(np.isnan(array),0,array)
    angle = 200

    with pytest.raises(ValueError) as err:
        preparation_data.projection_0_180(angle,array_corr)
    assert str(err.value) == 'the maximum angle for the tomography must be 180 or 360 degrees'
