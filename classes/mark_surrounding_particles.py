#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 09:37:30 2022

@author: Jannik Guckel, Daesung Park
"""
import numpy as np

def mark_surrounding_particles(CArray, aggc_pos, distance): #helping function
    agg_positions = []
    xy_coords = CArray[0, :, 0:2]
    for i in aggc_pos:
        agg_positions.append(i)
        for m in np.arange(0, xy_coords.shape[0]):
            if i == m:
                pass  
            else:
                dist = np.linalg.norm(xy_coords[i, :] - xy_coords[m, :], ord = 2 )
                if dist < distance:
                    agg_positions.append(m)
    
    #remove duplicates from list
    agg_positions = np.unique(agg_positions).tolist()
    agg_positions = [int(i) for i in agg_positions]
    return agg_positions