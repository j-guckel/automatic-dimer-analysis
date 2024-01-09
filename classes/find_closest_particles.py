#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 09:34:19 2022

@author: Jannik Guckel, Daesung Park
"""

import numpy as np


def find_closest_particles(CArray): #CArray = houghcircles_output
    xy_coords = CArray[0, :, 0:2]
    min_dists = []
    for i in np.arange(0, xy_coords.shape[0]):
        dists = np.zeros(xy_coords.shape[0])
        for j in np.arange(0, xy_coords.shape[0]):
            if i == j:
                dists[j] = 1e16   #simpyl add a large number to prevent it to be detected as minimum
            else:
                dists[j] = np.linalg.norm(xy_coords[i, :] - xy_coords[j, :], ord = 2 )
        minimum = i, np.nanmin(dists), np.nanargmin(dists)
        min_dists.append(minimum)
    min_dists = np.asarray(min_dists)
    #now sort values from small to big in column 0
    #min_dists = min_dists[min_dists[:,0].argsort(kind='mergesort')]
    return min_dists