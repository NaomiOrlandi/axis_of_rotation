import matplotlib.pyplot as plt
import neutompy as ntp
import image_slicer
import numpy as np
import os
import cv2
from matplotlib.offsetbox import AnchoredText
import SimpleITK as sitk
from tqdm import tqdm



def draw_ROI (img,title,ratio=0.85):
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
    file_data = open(os.path.join(datapath,'data.txt'),'a')
    file_data.write('rowmin {0} \nrowmax {1} \ncolmin {2} \ncolmax {3}'.format(rowmin,rowmax,colmin,colmax))
    file_data.close()


def cropping (img_stack,rowmin,rowmax,colmin,colmax):
    if rowmin <= rowmax and colmin <= colmax:
        for i in range(img_stack.shape[0]):
            img_stack_cropped = img_stack[:,rowmin:rowmax,colmin:colmax].astype(np.float32)
        return img_stack_cropped
    else:
        raise ValueError ('rowmin and colmin must be less than rowmax and colmax rispectively')

def normalization_with_ROI (img_stack,dark_stack,flat_stack,rowmin,rowmax,colmin,colmax):
    if img_stack.shape == dark_stack.shape and img_stack.shape == flat_stack.shape:
        ROI_coor = (rowmin,rowmax,colmin,colmax)
        if rowmin <= rowmax and colmin <= colmax:
            img_stack_norm = ntp.normalize_proj(img_stack,dark_stack,flat_stack,dose_draw=False,crop_coor=ROI_coor,crop_draw=False)
            return img_stack_norm
        else:
            raise ValueError ('rowmin and colmin must be less than rowmax and colmax rispectively')
    else:
        raise ValueError('the stack of images (tomographic projections,flat images and dark images) must have the same dimensions')

def normalization_no_ROI (img_stack,dark_stack,flat_stack):
    if img_stack.shape == dark_stack.shape and img_stack.shape == flat_stack.shape:
        img_stack_norm = ntp.normalize_proj(img_stack,dark_stack,flat_stack,dose_draw=False,crop_draw=False)
        return img_stack_norm
    else:
        raise ValueError('the stack of images (tomographic projections,flat images and dark images) must have the same dimensions')

def outliers_filter (img_stack, radius_2D_neighborhood, axis=0, k=1.0, out=None):
    ans = input('> Do you want to perform a filtering from bright outliers,dark outliers or both?\
     \n[B] filter just bright outliers\
     \n[D] filter just dark outliers\
     \n[A] filter both bright and dark outliers\
     \nType your answer and press [Enter] :')
    if ans == 'B' or ans == 'b':
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,'local',axis=0,outliers='bright',k=1)
    elif ans == 'D' or ans == 'd':
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,'local',axis=0,outliers='dark',k=1)
    elif ans == 'A' or ans == 'a':
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,'local',axis=0,outliers='bright',k=1)
        img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,'local',axis=0,outliers='dark',k=1)
    else:
        raise IOError('Input not valid.')
    
    return img_stack_filtered
    

#def find_center_of_rotation (proj_0, proj_180, nroi=None, ref_proj=None, ystep=5, ShowResults=False):
#    middle_shift,theta = ntp.find_COR(proj_0, proj_180, nroi=None, ref_proj=None, ystep=5, ShowResults=False)
#    return middle_shift,theta

#def correct_images (img_stack, proj_0, proj_180,datapath, show_opt='zero', shift=None, theta=None, nroi=None, ystep=5):
#    img_stack_corrected,shift,theta = ntp.correction_COR(img_stack, proj_0, proj_180, show_opt='zero', shift=None, theta=None, nroi=None, ystep=5)
#    image_slicer.plot_tracker(img_stack_corrected)
#    file_data = open(os.path.join(datapath,'data.txt'),'a')
#    file_data.write('\nshift {0} \ntilt angle {1}'.format(shift,theta))
#    file_data.close()
#    return img_stack_corrected



def ROIs_for_correction(ref_proj,ystep=5):
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
        m = par[1]
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


	#~ p0_r = np.roll(rotate(proj_0, theta, preserve_range=True,order=0, mode='edge'),    middle_shift , axis=1)
	#~ p90_r = np.roll(rotate(proj_180, theta, preserve_range=True, order=0, mode='edge'),  middle_shift, axis=1)
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
    ans = input('> Rotation axis found. Do you want to correct all projections?\
         \n[Y] Yes, correct them.  \n[N] No, find it again.\
         \n[C] Cancel and abort the script.\
         \nType your answer and press [Enter] :')
    return ans

def correction_axis_rotation (img_stack,shift,theta,datapath):
    
    print('> Correcting rotation axis misalignment...')
    for s in tqdm(range(0, img_stack.shape[0]), unit=' images'):
        img_stack[s,:,:] = np.roll(ntp.rotate_sitk(img_stack[s,:,:], theta, interpolator=sitk.sitkLinear), shift, axis=1)
    
    image_slicer.plot_tracker(img_stack)
    print('>Writing shift and theta values in data.txt file...')
    file_data = open(os.path.join(datapath,'data.txt'),'a')
    file_data.write('\nshift {0} \ntilt angle {1}'.format(shift,theta))
    file_data.close()
    return img_stack

def save_images (new_fname,img_stack,digits):
    print('Saving the corrected images...')
    ntp.write_tiff_stack(new_fname,img_stack, axis=0, start=0, croi=None, digit=digits, dtype=None, overwrite=False)