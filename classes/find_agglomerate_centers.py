#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 09:36:45 2022

@author: Jannik Guckel, Daesung Park
"""

import numpy as np

def find_agglomerate_centers(CArray, distance, agg_criterion): #helping function
    aggc_positions = []
    for i in np.arange(agg_criterion.shape[0]):
        if agg_criterion[i] < distance:
            aggc_positions.append(i)
    aggc_positions = [int(i) for i in aggc_positions]
    return aggc_positions