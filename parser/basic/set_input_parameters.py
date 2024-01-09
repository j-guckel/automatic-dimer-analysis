#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 10:55:24 2022

@author: Jannik Guckel, Daesung Park
"""
import ast

home_path = input('Working directory of your data. Absolute path is preferred. Make sure the directory ends on a separator (e.g. /) for Linux : ')
folder = input('Relative Path to a folder within the working directory. The images located in this folder will be analyzed. Make sure to include the separator : ')
full_path = home_path + folder
save_folder = input('Name of the folder, where the data will be saved. This folder will be located on the plane of the working directory. Separator must be included. WARNING: Leaving this empty may overwrite your original data! : ')
save_location = home_path + save_folder + folder

file_format = input('name of the file format you wish to analyze (without the . in front of it). tested formats: png, jpeg, tif, dm4, hdf5 : ')
    
pixelsize = float (input('size of a pixel (Square Pixel). Unit will be asked in the next question : ') )
pixel_unit = input('Unit of the Pixel Size, e.g. nm : ')
    
print('We use OpenCVs CHT for analysis. Therefore we temporarily convert the image into 8-bit. Intensity values should therefore be chosen with this in mind : ')
p1 = int( input('Gradient Threshold for Canny Edge filter of OpenCV. Integer Values between 0 and 255 are allowed, as OpenCV works in 8-bit : ') )
p2 =  int( input('Voting Threshold for positive circle detection. Integer Values allowed. Higher values means less detection results.: ') )
rmin = int( input('Minimum estimated radius of your particles (in Pixels, integer) : ') )
rmax = int( input ('Maximum estimated radius of your particles (in Pixels, integer) : ') )
particle_overlap_factor = float( input ('Particle overlap factor P. P * rmin determines a minimum distance between 2 particles (float) : ') )
monomer_radius = int( input ('maximum distance between dimer particles dmax (float, unit identical to pixel size) : ') )

use_additional_options = input('Customize other parameters? (y/n) Choosing n will use default parameters : ')
    
#default parameters of program. These are used if the option no is selected.
gauss_sigma = 2  
data_bar_length = 0
#Thresholding parameters
use_top_threshold = False
use_bottom_threshold = False
dehalo = False 
top_threshold = 1.0
bottom_threshold = 0.0
agg_size = 2
    
if use_additional_options == 'y':
        modify_image_preprocessing = input('Modify pre-processing routines? (y/n) : ')
        apply_thresholding = input('Do you want to apply intensity thresholding to the images? (y/n), default n : ')
       
        agg_size = int( input ('How strict should the agglomeration be? Integer values of 2 or higher are allowed. Default: 2. :') )
       
        gauss_sigma = float( input('Standard deviation of a Gaussian Kernel for optional Despiking. Choosing 0 disables this option. : ') ) if modify_image_preprocessing == 'y' else gauss_sigma
        data_bar_length = int( input('Height of the data bar in pixel (integer). This will remove the bottom rows of the image. Choosing 0 will disable this. : ') ) if modify_image_preprocessing == 'y' else data_bar_length
        use_top_threshold = bool( ast.literal_eval( input('Do you want to apply top thresholding? (1 for yes, 0 for no): ') ) ) if apply_thresholding == 'y' else use_top_threshold
        use_bottom_threshold = bool ( ast.literal_eval (input('Do you want to apply bottom thresholding? (1 for yes, 0 for no).') ) ) if apply_thresholding == 'y' else use_bottom_threshold
        top_threshold = ast.literal_eval (input ('Enter top threshold value. Float values between 0.0 and 1.0 will use the respective gray value quantile, integer values will use an absolute gray value (between 0 and 255) : ') ) if use_top_threshold is True else 1.0
        bottom_threshold = ast.literal_eval (input ('Enter bottom threshold value Float values between 0.0 and 1.0 will use the respective gray value quantile, integer values will use an absolute gray value (between 0 and 255) : ') ) if use_bottom_threshold is True else 0.0
        
        dehalo = bool ( ast.literal_eval (input('Do you to use Dehalo routine? (1 for yes, 0 for no). Use is recommended.: ') ) ) if use_top_threshold is True and use_bottom_threshold is True else dehalo
