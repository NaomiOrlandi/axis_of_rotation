import matplotlib.pyplot as plt
import neutompy as ntp
import numpy as np
import cv2
from matplotlib.offsetbox import AnchoredText
import SimpleITK as sitk
from neutompy.preproc.preproc import rotate_sitk as rotate_sitk


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

    p0_r = np.roll(rotate_sitk(proj_0, theta, interpolator=sitk.sitkLinear),    middle_shift , axis=1) 
    p90_r = np.roll(rotate_sitk(proj_180, theta, interpolator=sitk.sitkLinear),  middle_shift, axis=1)


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

def user_choice_for_correction ():
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