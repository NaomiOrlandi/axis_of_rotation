import cv2
import glob
import numpy as np
from matplotlib import pyplot as plt 
import ipywidgets as ipyw

import numpy as np
import matplotlib.pyplot as plt
import neutompy
from numpy.core.numeric import empty_like 

from image_slicer import IndexTracker



image_list = []
file_path = "C:/Users/Naomi/pythonproj/Tomografia_Darth_Vader/*.tiff" 
flat_path = "C:/Users/Naomi/pythonproj/Flat_Dark_Darth_Vader/Flat.tiff"
dark_path = "C:/Users/Naomi/pythonproj/Flat_Dark_Darth_Vader/Dark.tiff"
last_angle = 2*np.pi


for filename in glob.glob(file_path): #assuming tiff
    im=cv2.imread(filename,0) #0 stands for the gray_image reading (default is RGB reading)
    image_list.append(im)

projections = np.asarray(image_list)
'''
#show original images
fig, ax = plt.subplots(1, 1)
tracker = IndexTracker(ax, projections)
fig.canvas.mpl_connect('key_press_event', tracker.on_scroll)
plt.show()
'''
#preprocessing:rebinning,normalization,remove outliers,crop

#projections_binned = neutompy.rebin(projections, (1,2,2)) #binning
#print(projections_binned.shape)


proj_0 = projections[0,:,:]
proj_180 = projections[int(projections.shape[0]/2),:,:]
#print(proj_0.shape)

rowmin,rowmax,colmin,colmax = neutompy.draw_ROI(proj_0, 'ROI from projection_0', ratio=0.85) #draw ROI where light is detected

flat = cv2.imread(flat_path,0)
dark = cv2.imread(dark_path,0)
flat_stack = np.full(projections.shape,flat)
dark_stack = np.full(projections.shape,dark)

#print(flat_array.shape,dark_array.shape)


projections_norm = np.array(empty_like)
projections_norm,projections_norm_180 = neutompy.normalize_proj(projections, dark_stack, flat_stack, proj_180=proj_180, out=projections_norm, dose_file='', dose_coor=(), dose_draw=False, crop_file='', crop_coor=(rowmin,rowmax,colmin,colmax), crop_draw=False, scattering_bias=0.0, minus_log_lowest_val=None, min_denom=1e-06, min_ratio=1e-06, max_ratio=10.0, mode='median', log=False, sino_order=False)
'''
#show normalized images
fig1, ax = plt.subplots(1, 1)
tracker = IndexTracker(ax, projections_norm)
fig1.canvas.mpl_connect('key_press_event', tracker.on_scroll)
plt.show()
'''

projections_norm_outlier_filtered = neutompy.remove_outliers_stack(projections_norm,3,'local',outliers='bright')
projections_norm_outlier_filtered = neutompy.remove_outliers_stack(projections_norm,3,'local',outliers='dark')



middle_shift,theta = neutompy.find_COR(projections_norm_outlier_filtered[0,:,:],projections_norm_outlier_filtered[int(projections.shape[0]/2),:,:]) #find center of rotation


#chiedere se voglio fare la correzione o meno
print('Do you want to perform the correction for all the projections in the stack? (y/n)')

answer = input()
if answer == 'y':
    projections_norm_filtered_corrected = neutompy.correction_COR(projections_norm_outlier_filtered,projections_norm_outlier_filtered[0,:,:],projections_norm_outlier_filtered[int(projections.shape[0]/2),:,:],shift=middle_shift,theta=theta)
elif answer == 'n':
    print('Try again with different preprocessing!')
else:
	print('Not valid input. You should write or y or n')



'''
#show corrected images
fig2, ax = plt.subplots(1, 1)
tracker = IndexTracker(ax, projections_norm_filtered_corrected)
fig2.canvas.mpl_connect('key_press_event', tracker.on_scroll)
plt.show()
'''