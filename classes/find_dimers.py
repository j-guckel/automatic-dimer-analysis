#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 09:42:40 2022

@author: Jannik Guckel, Daesung Park
"""

import numpy as np
from classes.find_closest_particles import find_closest_particles
       
def find_dimer(CArray, min_dists, dimer_dist):
    dimer_list = []
    dimer_positions = []
    
    min_dists2 = min_dists[min_dists[:,1].argsort(kind='mergesort')] #sort distances from small to big
    
    for i in np.arange(0, min_dists.shape[0]-1):
        if min_dists2[i, 1] == min_dists2[i + 1, 1]:
            c1 = min_dists2[i, 0]
            c1p = min_dists2[i, 2]
            c2 = min_dists2[i+1, 0]
            c2p = min_dists2[i+1, 2]
            if c1 == c2p and c2 == c1p and min_dists2[i, 1] <= dimer_dist: #A and B are closest to each other
                #print(CArray[0, int(c1), :]), print(CArray[0, int(c2),:])
                dimer_info = tuple(CArray[0, int(c1), :].tolist() + CArray[0, int(c2),:].tolist()+
                                   [min_dists2[i, 1]])#, min_dists2[i+1, 0]])
                dimer_list.append(dimer_info)
                dimer_positions.append(c1)
                dimer_positions.append(c2)
    #print('creating position list')        
    dimer_positions = [int(i) for i in dimer_positions]        
    #now its time to delete the dimer
    #print('modifying NN distances')
    reduced_CArray = np.zeros(CArray.shape)
    reduced_CArray[:, :, :] = CArray[:, :, :]
    reduced_min_dists = np.zeros(min_dists.shape) #this is to avoid unbound local error
    reduced_min_dists = min_dists[:, :]
    
    for m in dimer_positions:
        reduced_CArray[0, m, :] = np.nan
    reduced_min_dists = find_closest_particles(reduced_CArray)
    return reduced_CArray, reduced_min_dists, dimer_list, dimer_positions


def check_for_equidistant_dimers(CArray, min_dists, dimer_dist):
    dimer_list = []
    dimer_positions = []

    for i in np.arange(0, min_dists.shape[0]):
        if min_dists[i, 0] != min_dists[i, 2]:
            try:
                A = int(np.where(min_dists[:, 2] == i)[0][0])
                #conditions
                cond1 = (min_dists[i, 0] == min_dists[A, 2])
                cond2 = (min_dists[A, 0] == min_dists[i, 2])
                cond3 = (min_dists[i, 1] <= dimer_dist)
                cond4 = (min_dists[i, 1] == min_dists[A, 1])
                cond5 = (i < A) #to prevent double counting
                
                conds = [cond1, cond2, cond3, cond4, cond5]
                if np.all(conds) == True:
                    dimer_positions.append(i)
                    dimer_positions.append(A)
                    dimer_info = tuple(CArray[0, i, :].tolist() + CArray[0, A,:].tolist()+
                                       [min_dists[i, 1]])#, min_dists2[i+1, 0]])
                    dimer_list.append(dimer_info)
            except:
                IndexError() #ignore if no partner is found
            
       
    dimer_positions = [int(i) for i in dimer_positions]    
    
    reduced_CArray = np.zeros(CArray.shape)
    reduced_CArray[:, :, :] = CArray[:, :, :]
    reduced_min_dists = np.zeros(min_dists.shape) #this is to avoid unbound local error
    reduced_min_dists = min_dists[:, :]
    
    for m in dimer_positions:
        reduced_CArray[0, m, :] = np.nan
    reduced_min_dists = find_closest_particles(reduced_CArray)
    return reduced_CArray, reduced_min_dists, dimer_list, dimer_positions    
