#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 09:41:41 2022

@author: Jannik Guckel, Daesung Park
"""
import numpy as np
from classes.find_closest_particles import find_closest_particles
               
def find_monomer(CArray, min_dists, distance): #min_dists = output of previous function
    monomer_list = []
    monomer_positions = []
    for i in np.arange(0, min_dists.shape[0]):
        if min_dists[i, 1] > distance and min_dists[i, 1] != 1e16:
            monomer_list.append(CArray[0, i, :])
            monomer_positions.append(i)
    monomer_positions = [int(i) for i in monomer_positions]
   
    reduced_CArray = np.zeros(CArray.shape)
    reduced_CArray[:, :, :] = CArray[:, :, :]
    reduced_min_dists = np.zeros(min_dists.shape)
    reduced_min_dists = min_dists[:, :]
    
    
    for m in monomer_positions:#
            reduced_CArray[0, m, :] = np.nan
    reduced_min_dists = find_closest_particles(reduced_CArray)
    
    return reduced_CArray, reduced_min_dists, monomer_list, monomer_positions
    