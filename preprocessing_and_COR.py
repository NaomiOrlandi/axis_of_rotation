from matplotlib.pyplot import plot
import neutompy as ntp
from numpy.core.numeric import empty_like
import image_slicer
import cv2
import numpy as np


def draw_ROI (proj_0):
    rowmin,rowmax,colmin,colmax = ntp.draw_ROI(proj_0, 'ROI from projection_0', ratio=0.85)
    return rowmin,rowmax,colmin,colmax

def normalization_with_ROI (img_stack,dark_stack,flat_stack,rowmin,rowmax,colmin,colmax):
    ROI_coor = (rowmin,rowmax,colmin,colmax)
    img_stack_norm = ntp.normalize_proj(img_stack,dark_stack,flat_stack,dose_draw=False,crop_coor=ROI_coor,crop_draw=False)
    return img_stack_norm

def normalization_no_ROI (img_stack,dark_stack,flat_stack):
    img_stack_norm = ntp.normalize_proj(img_stack,dark_stack,flat_stack,dose_draw=False,crop_draw=False)
    return img_stack_norm

def outliers_filter (img_stack, radius_2D_neighborhood, axis=0, k=1.0, out=None):
    img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,'local',axis=0,outliers='bright',k=1)
    img_stack_filtered = ntp.remove_outliers_stack(img_stack,radius_2D_neighborhood,'local',axis=0,outliers='dark',k=1)
    return img_stack_filtered

def find_center_of_rotation (proj_0, proj_180, nroi=None, ref_proj=None, ystep=5, ShowResults=False):
    middle_shift,theta = ntp.find_COR(proj_0, proj_180, nroi=None, ref_proj=None, ystep=5, ShowResults=False)
    return middle_shift,theta

def correct_images (img_stack, proj_0, proj_180, show_opt='zero', shift=None, theta=None, nroi=None, ystep=5):
    img_stack_corrected = ntp.correction_COR(img_stack, proj_0, proj_180, show_opt='zero', shift=None, theta=None, nroi=None, ystep=5)
    image_slicer.plot_tracker(img_stack_corrected)
    return img_stack_corrected

def save_images (new_fname,img_stack,digits):
    ntp.write_tiff_stack(new_fname,img_stack, axis=0, start=0, croi=None, digit=digits, dtype=None, overwrite=False)

def cropping (img_stack,rowmin,rowmax,colmin,colmax):
    for i in range(img_stack.shape[0]):
        img_stack_cropped = img_stack[:,rowmin:rowmax,colmin:colmax]
    return img_stack_cropped

