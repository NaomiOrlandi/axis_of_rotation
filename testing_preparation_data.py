import pytest
import preparation_data
import numpy as np

#=============================================
#UNIT TESTING
#=============================================

def test_reeder_gray_image_wrong_filepath ():
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
