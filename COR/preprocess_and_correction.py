import neutompy as ntp
import show_stack
import numpy as np
import os
import SimpleITK as sitk
from tqdm import tqdm
from neutompy.preproc.preproc import rotate_sitk as rotate_sitk


def save_ROI (rowmin,rowmax,colmin,colmax,datapath):
    '''
    This function creates or open a file called data.txt in the path datapath
    and save the coordinates of the ROI.
    
    Parameters
    ----------
    rowmin : int
        The minimum row coordinate
    rowmax : int
        The maximum row coordinate
    colmin : int
        The minimum column coordinate
    colmax : int
        The maximum column coordinate
    datapath : str
        string representing the directory path where to create data.txt 
    '''
    with open(os.path.join(datapath,'data.txt'),'a') as file:
        file.write('rowmin {0} \nrowmax {1} \ncolmin {2} \ncolmax {3}'.format(rowmin,rowmax,colmin,colmax))


def cropping (img_stack,rowmin,rowmax,colmin,colmax):
    '''
    This function crops all the images contained in a stack according to
    specific coordinates. It returns the new stack with the cropped images.
    
    Parameters
    ----------
    img_stack : ndarray
        3D array representing the stack of gray scaled images
    rowmin : int
        The minimum row coordinate
    rowmax : int
        The maximum row coordinate
    colmin : int
        The minimum column coordinate
    colmax : int
        The maximum column coordinate
    
    Returns
    -------
    img_stack_cropped : ndarray
        3D array containig the cropped images
    
    Raises
    ------
    ValueError
        if rowmin>rowmax or colmin>colmax
    '''
    print('> Cropping the images...')
    if rowmin <= rowmax and colmin <= colmax:
        for i in range(img_stack.shape[0]):
            img_stack_cropped = img_stack[:,rowmin:rowmax,colmin:colmax].astype(np.float32)
        return img_stack_cropped
    else:
        raise ValueError ('rowmin and colmin must be less than rowmax and colmax rispectively')


def normalization (img_stack,dark_stack,flat_stack):
    '''
    This function computes the normalization of all the the images (tomographic projections)
    of a stack, using a stack of dark images and one of flat images.
    It returns the new stack or normalized images.
    The fuction used is the neutompy.normalize_proj(proj, dark, flat,  proj_180=None, out=None,
    dose_file='', dose_coor=(), dose_draw=False,crop_file='', crop_coor=(), crop_draw=False,
    scattering_bias=0.0, minus_log_lowest_val=None,min_denom=1.0e-9,  min_ratio=1e-10, max_ratio=10.0,
    mode='mean', log=True,  sino_order=False, show_opt='mean'),
    where the dose ROI and the crop ROI are not considered.

    Parameters
    ----------
    img_stack : ndarray
        3D array containing the projection images
    dark_stack : ndarray
        3D array containing the dark images
    flat_stack : ndarray
        3D array containing the flat images

    Returns
    -------
    img_stack_norm : ndarray
        3D array containing the normalized images

    Raises
    ------
    ValueError
        if img_stack, dark_stack and flat_stack have different dimensions
    '''
    if img_stack.shape == dark_stack.shape and img_stack.shape == flat_stack.shape:
        img_stack_norm = ntp.normalize_proj(img_stack,dark_stack,flat_stack,dose_draw=False,crop_draw=False,min_denom=0.000000001,min_ratio=0.0000000001,log=True)
        return img_stack_norm
    else:
        raise ValueError('the stack of images (tomographic projections,flat images and dark images) must have the same dimensions')

def outliers_filter (img_stack, radius_2D_neighborhood, axis=0, k=1.0):
    '''
    This function removes bright or dark or both outliers from a stack of images.
    The algorithm elaborates 2d images and the filtering is iterated over all
    images in the stack.
    The function used is neutompy.remove_outliers_stack() and it replaces a pixel
    by the median of the pixels in the 2d neighborhood
    if it deviates from the median by more than a certain value (k*threshold).
    Threshold is set to 0.02, while k is an optional parameter.
    The user will be asked to choose the type of outliers to remove before the
    filtering.

    Parameters
    ----------
    img_stack : ndarray
        3D array containing the images to filter
    radius_2D_neighborhood : int or tuple of int
        The radius of the 2D neighborhood. The radius is defined separately for
        each dimension as the number of pixels that the neighborhood extends
        outward from the center pixel
    axis : int, optional
        The axis along wich the outlier removal is iterated.
        Default value is 0
    k : float, optional
        A pixel is replaced by the median of the pixels in the neighborhood
        if it deviates from the median by more than k*threshold.
        Default value is 1.0.

    Returns
    -------
    img_stack_filtered : ndarray
        3D array containing the filtered images

    Raises
    ------
    OSError
        if the user input is different from 'b','B','d','D','a' or 'A'
    '''
    ans = input('> Do you want to perform a filtering from bright outliers,dark outliers or both?\
     \n[B] filter just bright outliers\
     \n[D] filter just dark outliers\
     \n[A] filter both bright and dark outliers\
     \nType your answer and press [Enter] :')
    if ans == 'B' or ans == 'b':
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,threshold=0.02,axis=axis,k=k,outliers='bright')
    elif ans == 'D' or ans == 'd':
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,threshold=0.02,axis=axis,k=k,outliers='dark')
    elif ans == 'A' or ans == 'a':
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,threshold=0.02,axis=axis,k=k,outliers='bright')
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,threshold=0.02,axis=axis,k=k,outliers='dark')
    else:
        raise OSError('Input not valid.')
    
    return img_stack_filtered
    

def find_shift_and_tilt_angle(y_of_ROIs,proj_0,proj_180):
    '''
    This function estimates the offset and the tilt angle of the rotation axis with 
    respect to the detector using the projections at 0?? and at 180??.
    The latter is flipped horizontally and is compared with the projection
    at 0??, computing a root mean square error for each x position at each
    y coordinate considered.
    Hence the shift estimates for each y position are used to compute a polynomial 
    fit of degree 1, obtaining the shift and the tilt angle of the axis of rotation.
    Some algebrical operations are performed on these final values for costruction.

    References:
    [1] M. Yang, H. Gao, X. Li, F. Meng, D. Wei, "A new method todetermine the center
        of rotation shift in 2DCT scanning systemusing image cross correlation",
        NDT&E International, vol. 46 (2012), pp. 48-54
    [2] Anders P. Kaestner, "MuhRec???A new tomography reconstructor",
        Nuclear Instruments and Methods in Physics Research A 651 (2011) 156-160,
        section 2.2

    Parameters
    ----------
    y_of_ROIs : ndarray
        1D array of the y coordinates of the ROIs selected for the correction,
        with low noise and where the sample is visible
    proj_0 : ndarray
        2D array of the tomographic projection at 0??
    proj_180 : ndarray
        2D array of the tomographic projection at 180??
    
    Returns
    -------
    m : float
        slope of the polynomial fit between the shift and the corresponding y coordinate
    q : float
        intercept of the polynomial fit between the shift and the corresponding y coordinate
    shift : ndarray
        1D array containing the shift estimate for each y coordinate of y_of_ROIs
    offset : float
        shift of the axis of rotation with respect to the central vertical axis of the images
    middle_shift : int
        the offset value converted to integer
    theta : float
        the tilt angle of the rotation axis with respect to the central vertical axis of the images (in degrees) 
    
    Raises
    ------
    ValueError
        when the number of elements in y_of_ROIs is equal to 1, that is when the selected ROI
        has null height.
    '''

    if y_of_ROIs.size == 1:
        raise ValueError('ROI height must be greater than zero')
    else:
    
        tmin = - proj_0.shape[1]//2
        tmax =   proj_0.shape[1] - proj_0.shape[1]//2

        ny = proj_0.shape[0]
        nx = proj_0.shape[1]

        shift = np.zeros(y_of_ROIs.size)
        proj_180_flip = proj_180[:, ::-1]

        for y, slc in enumerate(y_of_ROIs):

            minimum = 1e7
            index_min = 0

		     # loop over the shift
            for t in range(tmin, tmax + 1):

                posy = np.round(slc).astype(np.int32)
                rmse = np.square( (np.roll(proj_0[posy], t, axis = 0) - proj_180_flip[posy]) ).sum() / nx

                if(rmse <= minimum):
                    minimum = rmse
                    index_min = t

            shift[y] = index_min
    

	    # perform linear fit
        par = np.polynomial.Polynomial.fit(y_of_ROIs, shift,1)
        par = par.convert().coef
        if len(par) == 2:      #case in which both offset and tilt angle are different from 0
            m = par[1]         #slope
            q = par[0]         #intercept
        elif len(par) == 1:    #case in which the tilt angle is 0??
            m = 0.0
            q = par[0]

    
	    # compute the tilt angle
        theta = np.arctan(0.5*m)   # in radians
        theta = np.rad2deg(theta)

	    # compute the shift
        offset       = (np.round(m*ny*0.5 + q)).astype(np.int32)*0.5
        middle_shift = (np.round(m*ny*0.5 + q)).astype(np.int32)//2


        print("Rotation axis Found!")
        print("offset =", offset, "   tilt angle =", theta, "??"  )

        return m,q,shift,offset,middle_shift, theta


def correction_axis_rotation (img_stack,shift,theta,datapath):
    '''
    This function performs the correction of all the images in the stack,
    according to the shift and tilt angle of the axis of rotation
    with respect to the central vertical axis of the images.
    The method also open the file data.txt placed in the path expressed by 
    datapath and write there the values of the shift and the tilt angle of
    the axis of rotation.
    Finally it returns the stack of corrected images.

    Parameters
    ----------
    img_stack : ndarray
        3D array containing the tomographic projection images to correct
    shift : int
        shift of the axis of rotation with respect to the central vertical axis of the images (in px)
    theta : float
        the tilt angle of the rotation axis with respect to the central vertical axis of the images (in degrees)
    datapath : str
        string representing the directory path where data.txt is placed
    
    Returns
    -------
    img_stack : ndarray
        3D array containing the corrected tomographic images
    '''
    
    print('> Correcting rotation axis misalignment...')
    for s in tqdm(range(0, img_stack.shape[0]), unit=' images'):
        img_stack[s,:,:] = np.roll(rotate_sitk(img_stack[s,:,:], theta, interpolator=sitk.sitkLinear), shift, axis=1)
    
    show_stack.plot_tracker(img_stack)
    print('>Writing shift and theta values in data.txt file...')

    with open(os.path.join(datapath,'data.txt'),'a') as file:
        file.write('\nshift {0} \ntilt angle {1}'.format(shift,theta))

    return img_stack

def save_images (new_fname,img_stack,digits):
    '''
    This function saves the stack of corrected images in the directory
    and with the filename prefix expressed by new_fname.

    Parameters
    ----------
    new_fname : str
        string representing the new files (.tiff images) path and the prefix of their name
    img_stack : ndarray
        3D array of the corrected images
    digits : int
        number of digits used for the numbering of the images
    '''
    print('Saving the corrected images...')
    ntp.write_tiff_stack(new_fname,img_stack, axis=0, start=0, croi=None, digit=digits, dtype=None, overwrite=False)