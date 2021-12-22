import pytest
import preprocessing_and_COR
import preparation_data
import numpy as np

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

