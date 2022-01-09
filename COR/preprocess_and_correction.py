import matplotlib.pyplot as plt
import neutompy as ntp
import show_stack
import numpy as np
import os
import cv2
from matplotlib.offsetbox import AnchoredText
import SimpleITK as sitk
from tqdm import tqdm



def draw_ROI (img,title,ratio=0.85):
    '''
    This function allows to select interactively a rectangular a region of interest (ROI)
    on an image and returns the coordinates of the ROI.
    The ROI should have width and height greater than zero to be selected.
    
    Parameters
    ----------
    img : ndarray
        2D array representing the image
    title : str
        title of the window where the user will select the ROI
    ratio : float,optional
        The filling ratio of the window respect to the screen resolution.
        It must be a number between 0 and 1. The default value is 0.85.
        
    Returns
    -------
    rowmin : int
        The minimum row coordinate
    rowmax : int
        The maximum row coordinate
    colmin : int
        The minimum column coordinate
    colmax : int
        The maximum column coordinate
        
    Raises
    ------
    ValueError
        if ratio is not greater than 0 and less or equal to 1
    ValueError
        if img is not a 2D array
    '''
    if not (0 < ratio <= 1):
        raise ValueError('The variable ratio must be between 0 and 1.')

    if (img.ndim != 2):
        raise ValueError("The image array must be two-dimensional.")

	# window size settings
    (width, height) = ntp.get_screen_resolution()
    scale_width = width / img.shape[1]
    scale_height = height / img.shape[0]
    scale = min(scale_width, scale_height)*ratio
    window_width = int(img.shape[1] * scale)
    window_height = int(img.shape[0] * scale)

    img = img.astype(np.float32)
    mu = np.nanmedian(img.ravel())
    finite_vals = np.nonzero(np.isfinite(img))
    s  = img[finite_vals].std()
    img = img/(mu+2*s)  # normalization can be improved
    imgshow = np.clip(img, 0, 1.0)

    condition = True
    while condition:
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(title,  window_width, window_height)
        r = cv2.selectROI(title, imgshow, showCrosshair = False, fromCenter = False)

        if (r == (0,0,0,0)):
            condition = True
            print('> ROI cancelled')
        elif r[2] == 0 or r[3] == 0:
            condition = True
            print('> ROI cancelled (ROI width or height must be greater that zero)')
        else:
            condition = False
			#print('> ROI selected ')
            rowmin, rowmax, colmin, colmax = r[1], r[1] + r[3], r[0], r[0] + r[2]
            print( 'ROI selected: ymin =', rowmin, ', ymax =', rowmax, ', xmin =', colmin, ', xmax =', colmax)
            cv2.destroyWindow(title)

    return rowmin, rowmax, colmin, colmax

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
    file_data = open(os.path.join(datapath,'data.txt'),'a')
    file_data.write('rowmin {0} \nrowmax {1} \ncolmin {2} \ncolmax {3}'.format(rowmin,rowmax,colmin,colmax))
    file_data.close()


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

def normalization_with_ROI (img_stack,dark_stack,flat_stack,rowmin,rowmax,colmin,colmax):
    '''
    This function computes the normalization of all the the images (tomographic projections)
    of a stack, using a stack of dark images and one of flat images.
    It will consider a ROI of all the images, whose coordinates are taken as parameters,
    and returns the new stack or normalized images.
    The fuction used is the neutompy.normalize_proj(proj, dark, flat,  proj_180=None, out=None,
    dose_file='', dose_coor=(), dose_draw=False,crop_file='', crop_coor=ROI_coor, crop_draw=False,
    scattering_bias=0.0, minus_log_lowest_val=None,min_denom=1.0e-6,  min_ratio=1e-6, max_ratio=10.0,
    mode='mean', log=False,  sino_order=False, show_opt='mean'),
    where the dose ROI is not considered,but the normalization
    is performed only on a region of interest (crop ROI) of all projections.
    The coordinates of the ROI are an input of the method.

    Parameters
    ----------
    img_stack : ndarray
        3D array containing the projection images
    dark_stack : ndarray
        3D array containing the dark images
    flat_stack : ndarray
        3D array containing the flat images
    rowmin : int
        The minimum row coordinate of the ROI
    rowmax : int
        The maximum row coordinate of the ROI
    colmin : int
        The minimum column coordinate of the ROI
    colmax : int
        The maximum column coordinate of the ROI
    
    Returns
    -------
    img_stack_norm : ndarray
        3D array containing the normalized images, each with the ROI dimensions
    
    Raises
    ------
    ValueError
        if rowmin>rowmax or colmin>colmax
    ValueError
        if img_stack, dark_stack and flat_stack have different dimensions
    '''
    if img_stack.shape == dark_stack.shape and img_stack.shape == flat_stack.shape:
        ROI_coor = (rowmin,rowmax,colmin,colmax) #create a tuple for the coordinates of the ROI
        if rowmin <= rowmax and colmin <= colmax:
            img_stack_norm = ntp.normalize_proj(img_stack,dark_stack,flat_stack,dose_draw=False,crop_coor=ROI_coor,crop_draw=False)
            return img_stack_norm
        else:
            raise ValueError ('rowmin and colmin must be less than rowmax and colmax rispectively')
    else:
        raise ValueError('the stack of images (tomographic projections,flat images and dark images) must have the same dimensions')

def normalization_no_ROI (img_stack,dark_stack,flat_stack):
    '''
    This function computes the normalization of all the the images (tomographic projections)
    of a stack, using a stack of dark images and one of flat images.
    It returns the new stack or normalized images.
    The fuction used is the neutompy.normalize_proj(proj, dark, flat,  proj_180=None, out=None,
    dose_file='', dose_coor=(), dose_draw=False,crop_file='', crop_coor=(), crop_draw=False,
    scattering_bias=0.0, minus_log_lowest_val=None,min_denom=1.0e-6,  min_ratio=1e-6, max_ratio=10.0,
    mode='mean', log=False,  sino_order=False, show_opt='mean'),
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
        img_stack_norm = ntp.normalize_proj(img_stack,dark_stack,flat_stack,dose_draw=False,crop_draw=False)
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
    The threshold used is 'local', hence the local standard deviation map is taken
    into account.
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
    IOError
        if the user input is different from 'b','B','d','D','a' or 'A'
    '''
    ans = input('> Do you want to perform a filtering from bright outliers,dark outliers or both?\
     \n[B] filter just bright outliers\
     \n[D] filter just dark outliers\
     \n[A] filter both bright and dark outliers\
     \nType your answer and press [Enter] :')
    if ans == 'B' or ans == 'b':
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,'local',axis=axis,k=k,outliers='bright')
    elif ans == 'D' or ans == 'd':
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,'local',axis=axis,k=k,outliers='dark')
    elif ans == 'A' or ans == 'a':
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,'local',axis=axis,k=k,outliers='bright')
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,'local',axis=axis,k=k,outliers='dark')
    else:
        raise IOError('Input not valid.')
    
    return img_stack_filtered
    

def ROIs_for_correction(ref_proj,ystep=5):
    '''
    This function allows to select one or multiple ROIs in the projections
    that will be considered when searching for the axis of rotation
    offset and tilt angle in the function find_shift_and_tilt_angle().
    The suggestion is to select the regions where the sample is visible
    and where there is as little noise as possible.
    The method returns a 1D array containing the values of y coordinate
    selected in the ROIs with a step defined by ystep. 

    Parameters
    ----------
    ref_proj : ndarray
        2D array representing the image where the user will select the ROIs
    ystep : int, optional
        the step between two successive y coordinates in the returned array

    Returns
    -------
    y_of_ROIs : ndarray
        1D array containing the y coordinates included in the selected ROIs
    '''
    print('To compute the rotation axis position it is necessary to select one or multiple regions where the sample is present.\nHence you must draw the different regions vertically starting from top to bottom.')
    while True:
        nroi = input('> Insert the number of regions to select: ')
        if(nroi.isdigit() and int(nroi)>0):
            nroi = int(nroi)
            break
        else:
            print('Not valid input.')
    
    #array containing that contains the y points within the rois selected by the user
    y_of_ROIs = np.array([], dtype=np.int32)

    # ROI selection
    for i in range(0, nroi):
		# print number of rois
        print('> Select ROI ' + str(i+1))
        title = 'Select region n. : ' + str(i+1)
        ymin, ymax, xmin, xmax = draw_ROI(ref_proj, title)
        
        y_ROI = np.arange(ymin, ymax +1, ystep)
        y_of_ROIs = np.concatenate((y_of_ROIs, y_ROI), axis=0)
        
    return y_of_ROIs

def find_shift_and_tilt_angle(y_of_ROIs,proj_0,proj_180):
    '''
    This function estimates the offset and the tilt angle of the rotation axis with 
    respect to the detector using the projections at 0° and at 180°.
    The latter is flipped horizontally and is compared with the projection
    at 0°, computing a root mean square error for each x position at each
    y coordinate considered.
    Hence the shift estimates for each y position are used to compute a polynomial 
    fit of degree 1, obtaining the shift and the tilt angle of the axis of rotation.
    Some algebrical operations are performed on these final values for costruction.

    References:
    [1] M. Yang, H. Gao, X. Li, F. Meng, D. Wei, "A new method todetermine the center
        of rotation shift in 2DCT scanning systemusing image cross correlation",
        NDT&E International 46 (2012) 48-54
    [2] Anders P. Kaestner, "MuhRec—A new tomography reconstructor",
        Nuclear Instruments and Methods in Physics Research A 651 (2011) 156-160,
        section 2.2

    Parameters
    ----------
    y_of_ROIs : ndarray
        1D array of the y coordinates of the ROIs selected for the correction,
        with low noise and where the sample is visible
    proj_0 : ndarray
        2D array of the tomographic projection at 0°
    proj_180 : ndarray
        2D array of the tomographic projection at 180°
    
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
        elif len(par) == 1:    #case in which the tilt angle is 0°
            m = 0.0
            q = par[0]

    
	    # compute the tilt angle
        theta = np.arctan(0.5*m)   # in radians
        theta = np.rad2deg(theta)

	    # compute the shift
        offset       = (np.round(m*ny*0.5 + q)).astype(np.int32)*0.5
        middle_shift = (np.round(m*ny*0.5 + q)).astype(np.int32)//2


        print("Rotation axis Found!")
        print("offset =", offset, "   tilt angle =", theta, "°"  )

        return m,q,shift,offset,middle_shift, theta

    

def graph_axis_rotation (proj_0,proj_180,y_of_ROIs,m,q,shift,offset,middle_shift,theta):
    '''
    This function shows two figures that report the results of find_shift_and_tilt_angle function.
    In the first figure are shown the computed shift of the rotation axis from the polynomial fit
    and the subtraction between the projection at 0° and the horizontal flip of the projection
    at 180° (proj_0 - pro_180[:,::-1]) before the correction.
    The second figure shows the difference image (proj_0 - pro_180[:,::-1]) after
	the correction and the histogram of the square of residuals between 
    proj_0 and the filpped proj_180.
    
    Parameters
    ----------
    proj_0 : ndarray
        2D array of the tomographic projection at 0°
    proj_180 : ndarray
        2D array of the tomographic projection at 180°
    y_of_ROIs : ndarray
        1D array of the y coordinates of the ROIs selected for the correction,
        with low noise and where the sample is visible
    m : float
        slope of the polynomial fit between the shift and the corresponding y coordinate
        (ref. find_shift_and_tilt_angle function)
    q : float
        intercept of the polynomial fit between the shift and the corresponding y coordinate
        (ref. find_shift_and_tilt_angle function)
    shift : ndarray
        1D array containing the shift estimate for each y coordinate of y_of_ROIs
        (ref. find_shift_and_tilt_angle function)
    offset : float
        shift of the axis of rotation with respect to the central vertical axis of the images (in px)
    middle_shift : int
        the offset value converted to integer 
    theta : float
        the tilt angle of the rotation axis with respect to the central vertical axis of the images (in degrees)
    '''

    proj_180_flip = proj_180[:, ::-1]

    p0_r = np.zeros(proj_0.shape, dtype=np.float32)
    p90_r = np.zeros(proj_0.shape, dtype=np.float32)

    ny = proj_0.shape[0]
    nx = proj_0.shape[1]

	# plot difference proj_0 - proj_180_flipped
    plt.figure('Analysis of the rotation axis position', figsize=(14,5), dpi=96)
    plt.subplots_adjust(wspace=0.5)
    ax1 = plt.subplot(1,2,1)

    diff = proj_0 - proj_180_flip
    mu = np.median(diff)
    s  = diff.std()

    plt.imshow(diff, cmap='gray', vmin=mu-s, vmax=mu+s)

    info_cor = 'offset = '  + "{:.2f}".format(offset) + '\n       θ = ' + "{:.3f}".format(theta)
    anchored_text1 = AnchoredText(info_cor, loc=2)
    ax1.add_artist(anchored_text1)

    plt.title(r'$P_0 - P^{flipped}_{\pi}$ before correction')
    plt.colorbar(fraction=0.046, pad=0.04)


    yaxis = np.arange(0, ny)
	# plot fit
    plt.plot( nx*0.5 - 0.5*m*yaxis - 0.5*q, yaxis,'b-')
	# plot data
    plt.plot( nx*0.5 - 0.5*shift, y_of_ROIs, 'r.', markersize=3)
	# draw vertical axis
    plt.plot([0.5*nx, 0.5*nx], [0, ny-1], 'k--' )

	# show results of the fit
    ax2 = plt.subplot(1,2,2)
    info_fit = 'shift = '  + "{:.3f}".format(m) + '*y + ' + "{:.3f}".format(q)
    anchored_text2 = AnchoredText(info_fit, loc=9)
    plt.plot(yaxis, m*yaxis + q, 'b-', label = 'fit')
    plt.plot(y_of_ROIs, shift, 'r.', label='data')
    plt.xlabel('$y$')
    plt.ylabel('shift')
    plt.title('Fit result')
    ax2.add_artist(anchored_text2)

    plt.legend()

    p0_r = np.roll(ntp.rotate_sitk(proj_0, theta, interpolator=sitk.sitkLinear),    middle_shift , axis=1) 
    p90_r = np.roll(ntp.rotate_sitk(proj_180, theta, interpolator=sitk.sitkLinear),  middle_shift, axis=1)


	# FIGURE with difference image and histogram
    plt.figure('Results of the rotation axis correction', figsize=(14,5), dpi=96)

    plt.subplot(1,2,1)
    plt.subplots_adjust(wspace=0.5)

    diff2 = p0_r - p90_r[:,::-1]
    mu = np.median(diff2)
    s  = diff2.std()
    plt.imshow(diff2 , cmap='gray', vmin=mu-s, vmax=mu+s)
    plt.title(r'$P_0 - P^{flipped}_{\pi}$ after correction')
    plt.colorbar(fraction=0.046, pad=0.04)



	# histogram of squares of residuals
    ax3 = plt.subplot(1,2,2)
    nbins = 1000
    row_marg = int(0.1*diff2.shape[0])
    col_marg = int(0.1*diff2.shape[1])
    absdif = np.abs(diff2)[row_marg:-row_marg, col_marg:-col_marg]
    [binning, width] = np.linspace(absdif.min(), absdif.max(), nbins, retstep=True)
    cc, edge = np.histogram(absdif, bins=binning)
    plt.bar(edge[:-1]+width*0.5, cc, width, color='C3', edgecolor='k', log=True)
    plt.gca().set_xscale("log")
    plt.gca().set_yscale("log")
    plt.xlim([0.01, absdif.max()])
    plt.xlabel('Residuals')
    plt.ylabel('Entries')
    plt.title('Histogram of residuals')

	# write text about residuals
    res =  np.abs(diff2).mean()
    info_res = r'$||P_0 - P^{flipped}_{\pi}||_1 / N_{pixel}$ = ' + "{:.4f}".format(res)
    anchored_text3 = AnchoredText(info_res, loc=1)
    ax3.add_artist(anchored_text3)

    print("average of residuals  = ", res)



    plt.show()

def question ():
    '''
    This function asks the user to choose whether to correct all the images [Y] 
    according to the computed shift and tilt angle of the axis of rotation
    with respect to the central vertical axis of the images,
    to not correct the images [N] and find again the shift and tilt angle of the axis
    of rotation, or to abort the script [C]
    '''
    ans = input('> Rotation axis found. Do you want to correct all projections?\
         \n[Y] Yes, correct them.  \n[N] No, find it again.\
         \n[C] Cancel and abort the script.\
         \nType your answer and press [Enter] :')
    return ans

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
        img_stack[s,:,:] = np.roll(ntp.rotate_sitk(img_stack[s,:,:], theta, interpolator=sitk.sitkLinear), shift, axis=1)
    
    show_stack.plot_tracker(img_stack)
    print('>Writing shift and theta values in data.txt file...')
    file_data = open(os.path.join(datapath,'data.txt'),'a')
    file_data.write('\nshift {0} \ntilt angle {1}'.format(shift,theta))
    file_data.close()
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