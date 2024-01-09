#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 14:58:10 2021

@author: Jannik Guckel, Daesung Park
"""

import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import re
from scipy.ndimage import gaussian_filter
from skimage.measure import label, regionprops
import csv
import hyperspy.api as hs

from classes.find_agglomerates import find_agglomerates
from classes.find_dimers import find_dimer, check_for_equidistant_dimers
from classes.find_monomers import find_monomer
from classes.find_closest_particles import find_closest_particles
from classes.find_ith_smallest_distance import find_ith_smallest_distance
import os
import shutil


'''This script is used if the image does not show origami structure and
only particle and substrate are visible'''

separator = '/'

#here insert question to import and input file!
read_input_file = input('Import Parameters from a file? (y/n)')
if read_input_file == 'y': #use pre-made input file!
    exec(open('./parser/basic/read_input_file.py').read())
else: #set the parameters on the fly.
    exec(open('./parser/basic/set_input_parameters.py').read()) 

full_path = home_path + folder
save_location = home_path + save_folder + folder

while os.path.isdir(home_path + save_folder) == True:
    overwrite = input('Analysis data has been found. Do you wish to overwrite? (y/n) : ')
    if overwrite == 'y':
        break
    if overwrite == 'n':
        save_folder = input('Enter new folder name : ')
        full_path = home_path + folder
        save_location = home_path + save_folder + folder
if os.path.isdir(home_path + save_folder) == False:
    os.mkdir(home_path + save_folder)

try:
    shutil.rmtree(save_location) 
except:
    FileNotFoundError()
os.mkdir(save_location)

exec(open('./parser/basic/save_input_params.py').read())


img_series = sorted(glob(('%s*.'+file_format)%(full_path))) 

distance = monomer_radius/pixelsize

#do not edit anything down below. the script might break otherwise
agg_list_tot = np.empty((0,4))
dimer_list_tot = np.empty((0,8))
monomer_list_tot = np.empty((0,4))
unidentified_list_tot = np.empty((0,4))

circle_list_tot = np.empty((0, 4))



if agg_size < 2:
    print('agg_size below 2 is chosen. The agglomeration search will be skipped!')

for alpha in np.arange(0, len(img_series)):
#for i in np.arange(4, 5):
    name = img_series[alpha].split('/')[-1].split('.')[0]


    try:  #this should work for all "image formats"
        img = Image.open(img_series[alpha]).convert('L') 
    except UnidentifiedImageError: #this should work for raw data formats (such as hdf5 and dm4)
        img = hs.load(img_series[alpha]).data   
    img = np.asarray(img)
    
    img = img if data_bar_length == 0 else img[:-data_bar_length, :] 

    
    img = gaussian_filter(img, sigma=gauss_sigma) 
    
    #find circles
    #Scale greyvalues, so max is at 255 for maxmimum contrast
    max_grey = np.amax(img)
    
    img = 255/max_grey * img
    img = img.astype(np.uint8)
    
    orig_img = np.zeros(img.shape)
    orig_img[:, :] = img[:, :]
    
    
    grey_list = img.ravel()   ###optional thresholding
    if use_top_threshold == True:     
        if type(top_threshold) == int:
            tth = top_threshold          
        if type(top_threshold) == float:
            tq = top_threshold      
            tth = np.quantile(grey_list, tq)    
        img[img>tth] = 0
    
    if use_bottom_threshold==True:     
        if type(bottom_threshold) == int:
            bth = bottom_threshold          
        if type(bottom_threshold) == float:
            bq = bottom_threshold      
            bth = np.quantile(grey_list, bq)    
        img[img<bth] = 0
        
    if any([use_bottom_threshold, use_top_threshold]) == True:
        threshold_image = np.zeros(img.shape)
        threshold_image[:, :] = img[:, :]
        plt.imsave(save_location + name + '_threshold_image'+ '.png', threshold_image, cmap='gray')
        
    if all([use_bottom_threshold, use_top_threshold, dehalo]) == True:
        binary_image = np.zeros(img.shape)
        binary_image[:, :] = img[:, :]
        binary_image[binary_image>0] = 255#binarize image in 8-bit
        binary_image=binary_image.astype(dtype = np.uint8)
        
        label_image = label(binary_image, connectivity= 1)  
        plt.imsave(save_location + name + '_clusters'+ '.png', label_image)
        cluster_threshold = 1.25 * np.pi*rmax**2   
        for i in np.arange(0, np.max(label_image), 1):
            cluster_size = np.count_nonzero(label_image == i)
            if cluster_size < cluster_threshold:
                label_image[label_image == i ] = 0
        
        
        label_image[label_image != 0] = 255
        plt.imsave(save_location + name + '_dehalo'+ '.png', label_image, cmap='gray')
        
        img[label_image == 0] = 0     #apply label image as mask to threshold image
    
    #Particle Detection
    min_part_dist = particle_overlap_factor * rmin
    
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, min_part_dist, #args are: Data/file, method, dp and minDist between centers
                               param1=p1, param2=p2,minRadius=rmin, maxRadius=rmax) #these parameters were determined by trial and error
    
    circles = np.empty((1, 0, 3)) if circles is None else circles
    CNumber = circles.shape[1]
    tot_circ = (circles.shape[1])
    
    CE_im = cv2.Canny(img, p1/2, p1) 
    plt.imsave(save_location + name + '_canny.png', CE_im)
    
    circles_bak = np.copy(circles[0])
    circles_bak = np.append(circles_bak, np.ones((circles_bak.shape[0], 1)) * alpha, axis = 1)
    
    
    circle_list_tot = np.append(circle_list_tot, circles_bak, axis = 0)

    
    plt.figure(num = 1, figsize=(15, 10))
    testimage = plt.imshow(orig_img, cmap='gray',vmin = 0, vmax = 255)
    fig = plt.gcf()
    ax = plt.gca()
    for i in np.arange(0, CNumber):
        ax.add_patch(plt.Circle((circles[0][i][0], circles[0][i][1]), circles[0][i][2], color = 'r', fill = False))
     
        tit_02 = '#%s total particles' %(tot_circ)
        ax.set_title("%s" %(tit_02))
    plt.savefig(save_location + name+'_hough_overlay'+'.png')
    plt.clf()
    plt.close()

    img[:, :] = orig_img[:, :]        
    
    
    with open(save_location + name + "_circles.csv", "w", newline="\n" ) as f:
            writer = csv.writer(f, delimiter =',')
            writer.writerow(['x, y, R'])
            writer.writerows(circles[0, :])
            f.close()

    #particle classification (basic)
    if circles.shape[1] == 0:
        pass
    else:
        reduced_coordinates = find_closest_particles(circles)
    
    
        if agg_size >= 2 and circles.shape[1] >= agg_size:
            print('executing agglomeration search')
            agg_crit = find_ith_smallest_distance(circles, agg_size-1) #this should stay invariant further down
            
            agg_rout = find_agglomerates(circles, reduced_coordinates, distance, agg_crit)
            circles = agg_rout[0]
            reduced_coordinates = agg_rout[1]
            agg_list1 = agg_rout[2]
            agg_positions1 = agg_rout[3]
        else:
            agg_list1 = []
            agg_positions1 = []
            
        print('executing monomer search #1')
        monomer_rout = find_monomer(circles, reduced_coordinates, distance)
        circles = monomer_rout[0]
        reduced_coordinates = monomer_rout[1]
        monomer_list1 = monomer_rout[2]
        monomer_positions1 = monomer_rout[3]
        
        print('executing dimer search #1')
        dimer_rout = find_dimer(circles, reduced_coordinates, distance)
        
        circles = dimer_rout[0]
        reduced_coordinates = dimer_rout[1]
        dimer_list1 = dimer_rout[2]
        dimer_positions1 = dimer_rout[3]
        
        print('executing monomer search #2')
        monomer_rout2 = find_monomer(circles, reduced_coordinates, distance)
        circles = monomer_rout2[0]
        reduced_coordinates = monomer_rout2[1]
        monomer_list2 = monomer_rout2[2]
        monomer_positions2 = monomer_rout2[3]
        
        print('executing dimer search #2')
        dimer_rout2 = find_dimer(circles, reduced_coordinates, distance)
        circles = dimer_rout2[0]
        reduced_coordinates = dimer_rout2[1]
        dimer_list2 = dimer_rout2[2]
        dimer_positions2 = dimer_rout2[3]
        
        dimer_rout3 = check_for_equidistant_dimers(circles, reduced_coordinates, distance)
        circles = dimer_rout3[0]
        reduced_coordinates = dimer_rout3[1]
        dimer_list3 = dimer_rout3[2]
        dimer_positions3 = dimer_rout3[3]
        
        #put the lists together
        agg_list = np.asarray(agg_list1)
        dimer_list = np.asarray(dimer_list1 + dimer_list2 +dimer_list3)
        monomer_list = np.asarray(monomer_list1 + monomer_list2)
        used_circles = agg_positions1 + monomer_positions1 + dimer_positions1 + monomer_positions2 + dimer_positions2 + dimer_positions3
        unidentified = np.delete(circles, used_circles, axis = 1)
        
        
        agg_list = np.append(agg_list, alpha * np.ones((agg_list.shape[0], 1)), axis = 1) if agg_list.shape[0] > 0 else agg_list  #don t try to append if list is empty. creates type errors
       
            
        
        dimer_list = np.append(dimer_list, alpha * np.ones((dimer_list.shape[0], 1)), axis = 1) if dimer_list.shape[0] > 0  else dimer_list
        
        
        monomer_list = np.append(monomer_list, alpha * np.ones((monomer_list.shape[0], 1)), axis = 1) if monomer_list.shape[0] > 0 else monomer_list
        
            
        unidentified = np.append(unidentified, alpha * np.ones((1, unidentified.shape[1], 1)), axis = 2) if unidentified.shape[1] > 0 else unidentified
        
        
        
        print('executing plot drawing')
        plt.figure(num = 2, figsize=(15, 10))
        testimage2 = plt.imshow(orig_img, cmap='gray',vmin = 0, vmax = 255)
        fig = plt.gcf()
        ax = plt.gca()
        
        try:
            for i in np.arange(0, agg_list.shape[0]):
                ax.add_patch(plt.Circle((agg_list[i][0], agg_list[i][1]), agg_list[i][2], color = 'm', fill = False))
        except:
            IndexError() # don t try to do this if there are no unidentified circles
        
        try:
            for i in np.arange(0, monomer_list.shape[0]):
                ax.add_patch(plt.Circle((monomer_list[i][0], monomer_list[i][1]), monomer_list[i][2], color = 'r', fill = False))
        except:
            IndexError()   
        
        try:
            for i in np.arange(0, dimer_list.shape[0]):
                ax.add_patch(plt.Circle((dimer_list[i][0], dimer_list[i][1]), dimer_list[i][2], color = 'g', fill = False))
                ax.add_patch(plt.Circle((dimer_list[i][3], dimer_list[i][4]), dimer_list[i][5], color = 'g', fill = False))
                ax.plot((dimer_list[i][0], dimer_list[i][3]), (dimer_list[i][1], dimer_list[i][4]), color = 'g')
        except:
            IndexError()
        try:
            for i in np.arange(0, unidentified.shape[1]):
                ax.add_patch(plt.Circle((unidentified[0][i][0], unidentified[0][i][1]), unidentified[0][i][2], color = 'b', fill = False))
        except:
            IndexError() 
        try:
            tit_00 = '%s' %(np.mean(dimer_list[:,-2])*pixelsize) + '+- %s' %(np.std(dimer_list[:,-2])*pixelsize) + ', #%s dimers'%(dimer_list.shape[0]) + ', #%s monomers'%(monomer_list.shape[0]) + ', #%s agglomerated'%(agg_list.shape[0]) +  ', #%s unidentified'%(unidentified[0].shape[0]) + ', #%s total' %(tot_circ)
            ax.set_title("%s" %(tit_00))
        except:
            IndexError()
        ax.set_xlim(0, img.shape[1])
        ax.set_ylim(img.shape[0], 0)
        plt.savefig(save_location + name+'_mono_dimer'+'.png')
        plt.clf()
        plt.close()
       
        
        ## for the total dimers in this folder
        try:
            agg_list_tot = np.append(agg_list_tot, agg_list, axis = 0)
        except:
            ValueError()
        try:    
            dimer_list_tot = np.append(dimer_list_tot, dimer_list, axis=0)
        except:
            ValueError()
        try:
            monomer_list_tot = np.append(monomer_list_tot, monomer_list, axis=0)
        except:
            ValueError()
        try:
            unidentified_list_tot = np.append(unidentified_list_tot, unidentified[0], axis=0)
        except:
            ValueError()
    
#plot image series results
fig, ax = plt.subplots(1, 1, figsize = (12.8, 9.6))    
ax.hist(np.array(dimer_list_tot[:, 6])*pixelsize, 50)
tit_01 = '%s' %(np.mean(dimer_list_tot[:, 6])*pixelsize) + '+- %s' %(np.std(dimer_list_tot[:,-2])*pixelsize) + ', #%s dimers'%(dimer_list_tot.shape[0]) + ', #%s monomers'%(monomer_list_tot.shape[0]) + ', #%s agglomerated'%(agg_list_tot.shape[0]) + ', #%s unidentified'%(unidentified_list_tot.shape[0])# + ', #%s total' %(tot_circ)
ax.set_title("%s" %(tit_01))
ax.set_xlabel('inter-particle distance d [' + str(pixel_unit) + ']')
ax.set_ylabel('Frequency')
plt.tight_layout()
plt.savefig(save_location + #folder +
            'total_distance_distribution.png')    


fig, ax = plt.subplots(1, 1, figsize = (12.8, 9.6))
ax.hist(np.array(circle_list_tot[ :, 2])*pixelsize, 10)
tit_01 = '%s' %(np.mean(circle_list_tot[:, 2])*pixelsize) + '+- %s' %(np.std(circle_list_tot[:,2])*pixelsize) + ', #%s particles'%(circle_list_tot.shape[0]) #
ax.set_title("%s" %(tit_01))
ax.set_xlabel('Particle radius [' + str(pixel_unit) + ']')
ax.set_ylabel('Frequency')
plt.tight_layout()
plt.savefig(save_location + #folder +
            'particle_size_distribution.png')    


index_list = circle_list_tot[:, 3].astype(int)
name_list = [img_series[index_list[i]].split(separator)[-1].split('\n')[0] for i in np.arange(0, index_list.shape[0], 1)]
name_list = np.asarray(name_list)
name_list = name_list.reshape((name_list.shape[0], 1))

index_list2 = dimer_list_tot[:, 7].astype(int)
name_list2 = [img_series[index_list2[i]].split(separator)[-1].split('\n')[0] for i in np.arange(0, index_list2.shape[0], 1)]
name_list2 = np.asarray(name_list2)
name_list2 = name_list2.reshape((name_list2.shape[0], 1))

with open(save_location + name + '_dimer_list.csv', 'w', newline = '\n' ) as h:
    writer = csv.writer(h, delimiter =',')
    writer.writerow(['The following coordinates are in image pixels!'])
    writer.writerow(['In order to obtain the real world distances, multiply with the pixelsize of', pixelsize, pixel_unit])
    writer.writerow(['x1', 'y1', 'R1', 'x2', 'y2', 'R2', 'dimer_dist', 'image_num', 'image name'])
    writer.writerows(np.append(dimer_list_tot, name_list2, axis = 1))
    h.close()
    
with open(save_location + name + '_all_circles_list.csv', 'w', newline = '\n' ) as h:
    writer = csv.writer(h, delimiter =',')
    writer.writerow(['The following coordinates are in image pixels!'])
    writer.writerow(['In order to obtain the real world distances, multiply with the pixelsize of', pixelsize, pixel_unit])
    writer.writerow(['x', 'y', 'R', 'image_num', 'image_name'])
    writer.writerows(np.append(circle_list_tot, name_list, axis = 1))
    h.close()    
    