#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 14:58:10 2021

@author: Jannik Guckel, Daesung Park
"""

    
'''This script is used if origami, particle and substrate are visible.'''

import hyperspy.api as hs
import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import re
from scipy.ndimage import gaussian_filter, median_filter, center_of_mass
from skimage.measure import label, regionprops
import csv
from classes.find_dimers import find_dimer, check_for_equidistant_dimers
from classes.find_monomers import find_monomer
from classes.find_agglomerates import find_agglomerates
from classes.find_closest_particles import find_closest_particles
from classes.find_ith_smallest_distance import find_ith_smallest_distance
#needs to be saved in same directory as this file
import os
import shutil


separator = '/'

#here insert question to import and input file!
read_input_file = input('Import Parameters from a file? (y/n)')
if read_input_file == 'y': #use pre-made input file!
    exec(open('./parser/with_origami/read_input_file.py').read())
else: #set the parameters on the fly.
    exec(open('./parser/with_origami/set_input_parameters.py').read()) 

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

exec(open('./parser/with_origami/save_input_params.py').read())

img_series = sorted(glob(('%s*.'+file_format)%(full_path))) 

distance = monomer_radius/pixelsize

#do not edit anything down below. the script might break otherwise

agg_size = 2
agg_list_tot = np.empty((0,4))
dimer_list_tot = np.empty((0,8)) # Create the total dimer list for the entire images.
monomer_list_tot = np.empty((0,4))
single_part_list_tot = np.empty((0,4))
unidentified_list_tot = np.empty((0,4))

origami_pos_tot = np.empty((0,3))
circle_list_tot = np.empty((0, 4))

for alpha in np.arange(0, len(img_series)):
#for i in np.arange(4, 5):
    name = img_series[alpha].split('/')[-1].split('.')[0]


    img = Image.open(img_series[alpha]).convert('L') #converts image to gray
    orig_img = np.copy(img)
    
     # pixel height of data bar (found out by trial and error)
    img = np.asarray(img)
    #img = np.flip(img, axis = 1)
    img = img[:-data_bar_length, :] if data_bar_length > 0 else img#remove databar
    
        
    
    img = gaussian_filter(img, sigma=gauss_sigma) 
    
    #find circles
    #Scale greyvalues, so max is at 255 for maxmimum contrast
    max_grey = np.amax(img)
    
    img = 255/max_grey * img
    img = img.astype(np.uint8) #you need 8 bit image input
    

    grey_list = img.ravel()
    if use_top_threshold == True:     
        if type(top_threshold) == int:
            tth = top_threshold          #tth is short for top threshold
        if type(top_threshold) == float:
            tq = top_threshold      #tq is short for top quantile
            tth = np.quantile(grey_list, tq)    
        img[img>tth] = 0
    
    if use_bottom_threshold==True:     #maybe do an automatic routine for this in the future?????
        if type(bottom_threshold) == int:
            bth = bottom_threshold          #bth is short for bottom threshold
        if type(bottom_threshold) == float:
            bq = bottom_threshold      #bq is short for bottom quantile
            bth = np.quantile(grey_list, bq)    
        img[img<bth] = 0
        
    if use_inverse_bandpass is True:
        #estimate top and bottom threshold in analogy to above
        if type(top_threshold) == int:
            tth = top_threshold          #tth is short for top threshold
        if type(top_threshold) == float:
            tq = top_threshold      #tq is short for top quantile
            tth = np.quantile(grey_list, tq) 
        
        if type(bottom_threshold) == int:
            bth = bottom_threshold          #bth is short for bottom threshold
        if type(bottom_threshold) == float:
            bq = bottom_threshold      #bq is short for bottom quantile
            bth = np.quantile(grey_list, bq)    
        
        top_img = (img < tth) #create a truth mask
        bottom_img = (img > bth)
        raw_bandpass = np.logical_and(top_img, bottom_img)
        

        halo_mask = median_filter(raw_bandpass, size = rmax)  
        #removes halos by median filtering. around the halo rings, the majority of pixels are either
        #origami or particle. this means the halos are rings of 1s surrounded my large amounts of zeros.
        # this means the median should be 0. a noisy pixel should be surrounded by substrate. the median therefore
        # should be 1.
        
        img[halo_mask] = 0
        
        

    
    
    if any([use_bottom_threshold, use_top_threshold, use_inverse_bandpass]) == True:
        threshold_image = np.zeros(img.shape)
        threshold_image[:, :] = img[:, :]
        plt.imsave(save_location + name + '_threshold_image'+ '.png', threshold_image, cmap='gray')
        
    if any([use_bottom_threshold, use_top_threshold, use_inverse_bandpass]) == True:
        binary_image = np.zeros(img.shape)
        binary_image[:, :] = img[:, :]
        binary_image[binary_image>0] = 255#binarize image in 8-bit
        binary_image=binary_image.astype(dtype = np.uint8)
        
        label_image = label(binary_image, connectivity= 1)  
        label_image2 = np.ma.masked_where(label_image == 0, label_image)
        plt.imsave(save_location + name + '_clusters'+ '.png', label_image2)
        #pixels with values of 0 are assumed to be background by default and thus the black background will always be cluster 0
        
        
        cluster_size_info = []
        for i in np.arange(1, np.max(label_image), 1):
            cluster_size = np.count_nonzero(label_image == i)
            cluster_size_info.append([i, cluster_size])
            if cluster_size < cluster_threshold:
                label_image[label_image == i ] = 0

        cluster_size_info = np.asarray(cluster_size_info)
        filtered_clusters = cluster_size_info[cluster_size_info[:, 1] > cluster_threshold]
        cluster_num_list = filtered_clusters[:, 0]
        cluster_size_list = filtered_clusters[:, 1]
        
        denoised_cluster_image = np.zeros(img.shape)
        denoised_cluster_image[:,:] = label_image[:,:]
        denoised_cluster_image[label_image != 0] = 255        #don t save this as label image, because you need the actual label image now
        plt.imsave(save_location + name + '_denoised_clusters'+ '.png', denoised_cluster_image, cmap='gray')
        
        denoised_cluster_image = denoised_cluster_image/255   #transforms into a mask
        denoised_masked = threshold_image * denoised_cluster_image
        denoised_masked = denoised_masked.astype(np.uint8)
        plt.imsave(save_location + name + '_masked.png', denoised_masked, cmap = 'gray')
        CE_im = cv2.Canny(denoised_masked, p1/2, p1) 
        plt.imsave(save_location + name + '_canny.png', CE_im)

        circles_img = np.empty((0, 3))
        monomer_list = []
        dimer_list = []
        agg_list = np.empty((0, 3))
        single_part_list = []
        unidentified = np.empty((0, 3))
        origami_pos = np.empty((0, 2))
        
        
        
        min_part_dist = particle_overlap_factor * rmin
        
        for c in cluster_num_list:
            index = np.where(cluster_num_list==c)[0][0]
            print('analyzing cluster', index+1, 'of ', len(cluster_num_list), 'in image', alpha+1, 'of', len(img_series))
            mask = np.zeros(label_image.shape)
            mask[:,:] = label_image[:, :]
            mask[mask != c ] = 0
            mask = mask/c     #transform it into 0,1 values
            
            if cluster_size_list[index] >= origami_threshold:
                cluster_center = center_of_mass(mask)  #uses i, j indexing
                cluster_x, cluster_y = cluster_center[1], cluster_center[0] #swaps to x, y indexing
                cc = np.asarray((cluster_x, cluster_y)). reshape((1, 2))
                origami_pos = np.append(origami_pos, cc, axis = 0)
            
            masked_image = threshold_image * mask  #this turns everything except the selected origami to 0
            masked_image = masked_image.astype(np.uint8)
            circles = cv2.HoughCircles(masked_image, cv2.HOUGH_GRADIENT, 1, min_part_dist, #args are: Data/file, method, dp and minDist between centers
                                   param1=p1, param2=p2,minRadius=rmin, maxRadius=rmax) #these parameters were determined by trial and error
            
            circles = np.empty((1, 0, 3)) if circles is None else circles
            circles_img = np.append(circles_img, circles[0], axis = 0)
            
            if circles.shape[1] == 1: #can only be monomer or single particle
                if cluster_size_list[index] >= origami_threshold:
                    monomer_list = monomer_list + circles[0].tolist()
                if cluster_size_list[index] < origami_threshold:
                    single_part_list = single_part_list + circles[0].tolist()
            if circles.shape[1] == 2: #can only be dimer or 2 monomers
                reduced_coordinates = find_closest_particles(circles)
                #execute a momomer check
                monomer_rout = find_monomer(circles, reduced_coordinates, distance)
                circles = monomer_rout[0]
                reduced_coordinates = monomer_rout[1]
                monomer_list1 = monomer_rout[2]
                monomer_positions1 = monomer_rout[3]
                #execute a dimer check
                dimer_rout = find_dimer(circles, reduced_coordinates, distance)
                circles = dimer_rout[0]
                reduced_coordinates = dimer_rout[1]
                dimer_list1 = dimer_rout[2]
                dimer_positions1 = dimer_rout[3]
                
                monomer_list = monomer_list + monomer_list1
                dimer_list = dimer_list + dimer_list1
                
                
                used_circles = dimer_positions1 + monomer_positions1
                circles = np.delete(circles, used_circles, axis = 1)
                
                unidentified = np.append(unidentified, circles[0], axis = 0)
                
            if circles.shape[1] > 2:
                reduced_coordinates = find_closest_particles(circles)
    
                #check for agglomerates. skip this step if you pick an agg size that is larger than the particles.
                if agg_size >= 2 and circles.shape[1] >= agg_size:
                    #print('executing agglomeration search')
                    agg_crit = find_ith_smallest_distance(circles, agg_size-1) #this should stay invariant further down
                    
                    agg_rout = find_agglomerates(circles, reduced_coordinates, distance, agg_crit)
                    circles = agg_rout[0]
                    reduced_coordinates = agg_rout[1]
                    agg_list1 = np.empty((0, 3)) if agg_rout[2] == [] else np.asarray(agg_rout[2])
                    agg_positions1 = agg_rout[3]
                else:
                    agg_list1 = np.empty((0, 3))
                    agg_positions1 = []
                
                #monomer search
                monomer_rout = find_monomer(circles, reduced_coordinates, distance)
                circles = monomer_rout[0]
                reduced_coordinates = monomer_rout[1]
                monomer_list1 = monomer_rout[2]
                monomer_positions1 = monomer_rout[3]
                    
                #dimer search
                dimer_rout = find_dimer(circles, reduced_coordinates, distance)
                    
                circles = dimer_rout[0]
                reduced_coordinates = dimer_rout[1]
                dimer_list1 = dimer_rout[2]
                dimer_positions1 = dimer_rout[3]
                
                ####SPECIAL CASE: after agg_search only 1 leftover particle.
                leftover_check = ~np.isnan(circles[0]).any(axis=1)
                leftover_num = np.count_nonzero(leftover_check)
                if leftover_num == 1:
                    monomer_positions1 = [np.where(leftover_check == True)[0][0]]
                    mono = circles[0][monomer_positions1].reshape((1, 3))
                    monomer_list = monomer_list + mono.tolist()
                
                
                
                    
                agg_list = np.append(agg_list, agg_list1, axis = 0)
                monomer_list = monomer_list + monomer_list1
                dimer_list = dimer_list + dimer_list1
                
                
                used_circles = dimer_positions1 + monomer_positions1 + agg_positions1
                circles = np.delete(circles, used_circles, axis = 1)
                
                unidentified = np.append(unidentified, circles[0], axis = 0)
        
                
    plt.figure(num = 1, figsize=(15, 10))
    testimage = plt.imshow(orig_img, cmap='gray',vmin = 0, vmax = 255)
    fig = plt.gcf()
    ax = plt.gca()
    for i in np.arange(0, circles_img.shape[0]):
        ax.add_patch(plt.Circle((circles_img[i][0], circles_img[i][1]), circles_img[i][2], color = 'r', fill = False))
         
        tit_02 = '#%s total particles' %((circles_img.shape[0]))
        ax.set_title("%s" %(tit_02))
    #plt.imsave(fig, 'hough_overlay.png')
    plt.savefig(save_location + name+'_hough_overlay'+'.png')
    plt.clf()
        
    with open(save_location + name + "_circles.csv", "w", newline="\n" ) as f:
        writer = csv.writer(f, delimiter =',')
        writer.writerow(['x', 'y', 'R'])
        writer.writerows(circles_img[:, :])
        f.close()
                
    num_list = alpha * np.ones((circles_img.shape[0], 1))
    circles_img = np.append(circles_img, num_list, axis = 1)
    circle_list_tot = np.append(circle_list_tot, circles_img, axis = 0)
                
    agg_list = np.asarray(agg_list)
    dimer_list = np.asarray(dimer_list)
    monomer_list = np.asarray(monomer_list)
    single_part_list = np.asarray(single_part_list)    
    unidentified = np.asarray(unidentified)
        
    agg_list = np.append(agg_list, alpha*np.ones((agg_list.shape[0], 1)), axis = 1) if agg_list.shape[0] > 0 else agg_list
    dimer_list = np.append(dimer_list, alpha * np.ones((dimer_list.shape[0], 1)), axis = 1) if dimer_list.shape[0] > 0  else dimer_list
    monomer_list = np.append(monomer_list, alpha * np.ones((monomer_list.shape[0], 1)), axis = 1) if monomer_list.shape[0] > 0 else monomer_list
    single_part_list = np.append(single_part_list, alpha * np.ones((single_part_list.shape[0], 1)), axis = 1) if single_part_list.shape[0] > 0 else single_part_list
    unidentified = np.append(unidentified, alpha * np.ones((unidentified.shape[0], 1)), axis = 1) if unidentified.shape[0] > 0 else unidentified
    origami_pos = np.append(origami_pos, alpha*np.ones((origami_pos.shape[0], 1)), axis = 1) if origami_pos.shape[0] > 0 else origami_pos
 
    
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
         for i in np.arange(0, single_part_list.shape[0]):
             ax.add_patch(plt.Circle((single_part_list[i][0], single_part_list[i][1]), single_part_list[i][2], color = 'orange', fill = False))
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
        for i in np.arange(0, unidentified.shape[0]):
            ax.add_patch(plt.Circle((unidentified[i][0], unidentified[i][1]), unidentified[i][2], color = 'b', fill = False))
    except:
        IndexError() # don t try to do this if there are no unidentified circles
            #also let it draw rectangles here
    try:
        tit_00 = '%s' %(np.mean(dimer_list[:,-2])*pixelsize) + '+- %s' %(np.std(dimer_list[:,-2])*pixelsize) + ', #%s dimers'%(dimer_list.shape[0]) + ', #%s monomers'%(monomer_list.shape[0]) + ', #%s single particles'%(single_part_list.shape[0]) + ', #%s agglomerated'%(agg_list.shape[0]) +  ', #%s unidentified'%(unidentified.shape[0]) + ', #%s total' %((circles_img.shape[0]))
        ax.set_title("%s" %(tit_00))
    except:
        IndexError()
    ax.set_xlim(0, img.shape[1])
    ax.set_ylim(img.shape[0], 0)
    plt.savefig(save_location + name+'_mono_dimer'+'.png')
    plt.clf()
    plt.close()   
      
    fig, ax = plt.subplots(1, 1, num = 3, figsize = (15, 10))
    ax.imshow(orig_img, cmap = 'gray')
    ax.scatter(origami_pos[:, 0], origami_pos[:, 1], s = 11, c='red', marker= 'x')
    ax.set_xlim(0, img.shape[1])
    ax.set_ylim(img.shape[0], 0)
    plt.savefig(save_location + name + 'origami_centers' + '.png')
    plt.clf()
    plt.close()
    
    ## for the total dimers in this folder
    try:
        agg_list_tot = np.append(agg_list_tot, agg_list, axis = 0)
    except:
        ValueError()  #don t try to append if you have no agglomerates
    try:    
        dimer_list_tot = np.append(dimer_list_tot, dimer_list, axis=0)
    except:
        ValueError()
    try:
        monomer_list_tot = np.append(monomer_list_tot, monomer_list, axis=0)
    except:
        ValueError()
    try:
        single_part_list_tot = np.append(single_part_list_tot, single_part_list, axis=0)
    except:
        ValueError()    
            
    try:
        unidentified_list_tot = np.append(unidentified_list_tot, unidentified, axis=0)
    except:
        ValueError()
    try:
        origami_pos_tot = np.append(origami_pos_tot, origami_pos, axis=0)
    except:
        ValueError()
    



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


index_list3 = origami_pos_tot[:, 2].astype(int)
name_list3 = [img_series[index_list3[i]].split(separator)[-1].split('\n')[0] for i in np.arange(0, index_list3.shape[0], 1)]
name_list3 = np.asarray(name_list3)
name_list3 = name_list3.reshape((name_list3.shape[0], 1))


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
    
with open(save_location + name + '_all_origami_center_list.csv', 'w', newline = '\n' ) as h:
    writer = csv.writer(h, delimiter =',')
    writer.writerow(['The following coordinates are in image pixels!'])
    writer.writerow(['In order to obtain the real world distances, multiply with the pixelsize of', pixelsize, 'nm'])
    writer.writerow(['xc', 'yc', 'image_num', 'image_name'])
    writer.writerows(np.append(origami_pos_tot, name_list3, axis = 1))
    h.close()