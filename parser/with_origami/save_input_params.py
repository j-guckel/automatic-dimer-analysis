#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 11:38:21 2022

@author: Jannik Guckel, Daesung Park
"""

import csv

with open(save_location + "_input_params.txt", "w", newline="\n" ) as g:
            writer = csv.writer(g, delimiter =',')
            writer.writerow(['[Program Information]'])
            writer.writerow(['Detection Type: with origami'])
            writer.writerow(['program version: 1.0 initial release'])
            
            writer.writerow(['[Data Information]'])
            writer.writerow(['Home Directory of Data: '])
            writer.writerow([home_path.split('\n')[0]])
            writer.writerow(['Relative Working Directory of the Data Subset:'])
            writer.writerow([folder.split('\n')[0]])
            writer.writerow(['Name of Results Folder: '])
            writer.writerow([save_folder.split('\n')[0]])
            writer.writerow(['Data Format: '])
            writer.writerow([file_format.split('\n')[0]])
            writer.writerow(['Pixel Size: '])
            writer.writerow([pixelsize])
            writer.writerow(['Unit of Pixel size: '])
            writer.writerow([pixel_unit.split('\n')[0]])
            
            writer.writerow(['[Detection Parameters]'])
            writer.writerow(['Canny Edge Detection Threshold p1 (8-bit unsigned integer) '])
            writer.writerow([p1])
            writer.writerow(['Voting Threshold p2 (integer)'])
            writer.writerow([p2])
            writer.writerow(['Min Radius (pixel): '])
            writer.writerow([rmin])
            writer.writerow(['Max Radius (pixel): '])
            writer.writerow([rmax])
            writer.writerow(['Particle Overlap Factor P (no unit) - minimum distance between neighboring particles = P * r: '])
            writer.writerow([particle_overlap_factor])
            writer.writerow(['Monomer radius dmax, float. unit identical pixel unit given earlier)'])
            writer.writerow([monomer_radius])
            writer.writerow(['Threshold for Noise Pixel cluster (pixel): '])
            writer.writerow([cluster_threshold])
            writer.writerow(['Threshold for origami cluster (pixel: '])
            writer.writerow([origami_threshold])

            writer.writerow(['[Segmentation Parameters]'])
            writer.writerow(['Background Segmentation Mode (0, 1, 2)'])
            writer.writerow(['if you edit the mode, you have to manually edit which thresholds to apply.'])
            writer.writerow(['Mode 0: Only top is active. Mode 1: only bottom is active. Mode 2: only inverse_bandpass is active'])
            writer.writerow([select_segmentation_mode])
            writer.writerow(['Use Bottom Threshold (bool): '])
            writer.writerow([use_bottom_threshold])
            writer.writerow(['Bottom Threshold: '])
            writer.writerow([bottom_threshold])
            writer.writerow(['use Top Threshold (bool): '])
            writer.writerow([use_top_threshold])
            writer.writerow(['Top Threshold: '])
            writer.writerow([top_threshold])
            writer.writerow(['use inverse bandpass (bool): '])
            writer.writerow([use_inverse_bandpass])

            writer.writerow(['[Pre-Processing Parameters]'])
            writer.writerow(['Standard Deviation Gaussian Blurring (no unit): '])
            writer.writerow([gauss_sigma])
            writer.writerow(['Databar Length (Pixel): '])
            writer.writerow([data_bar_length])
            
            
            g.close()
