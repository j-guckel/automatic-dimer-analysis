#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 09:35:41 2022

@author: Jannik Guckel, Daesung Park
"""

import numpy as np


def find_ith_smallest_distance(CArray, m): #additional failsafe
    xy_coords = CArray[0, :, 0:2]
    ith_smallest = []
    for i in np.arange(0, xy_coords.shape[0]):
        dists = np.zeros(xy_coords.shape[0])
        for j in np.arange(0, xy_coords.shape[0]):
            if i == j:
                dists[j] = 1e16   #simpyl add a large number to prevent it to be detected as minimum
            else:
                dists[j] = np.linalg.norm(xy_coords[i, :] - xy_coords[j, :], ord = 2 )
        dists2 = np.sort(dists) #sorts from small to big
        ith_smallest.append(dists2[m])
    ith_smallest = np.asarray(ith_smallest)
    return ith_smallest  