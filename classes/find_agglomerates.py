#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 09:40:16 2022

@author: Jannik Guckel, Daesung Park
"""
import numpy as np
from classes.find_agglomerate_centers import find_agglomerate_centers
from classes.mark_surrounding_particles import mark_surrounding_particles
from classes.find_closest_particles import find_closest_particles


               
def find_agglomerates(CArray, min_dists, distance, agg_criterion):
    centers = find_agglomerate_centers(CArray, distance, agg_criterion)
    agg_positions = mark_surrounding_particles(CArray, centers, distance)
    #extend marking around the edges
    agg_positions = mark_surrounding_particles(CArray, agg_positions, distance)    
    agg_list = []
    for i in agg_positions:
        agg_list.append(CArray[0, i, :])
        
    reduced_CArray = np.zeros(CArray.shape)
    reduced_CArray[:, :, :] = CArray[:, :, :]
    reduced_min_dists = np.zeros(min_dists.shape)
    reduced_min_dists = min_dists[:, :]
    
    
    for m in agg_positions:#
            reduced_CArray[0, m, :] = np.nan
    reduced_min_dists = find_closest_particles(reduced_CArray)
    
    return reduced_CArray, reduced_min_dists, agg_list, agg_positions
  