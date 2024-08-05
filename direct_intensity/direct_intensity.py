import os 
import re
import json
import numpy as np
import pandas as pd
from skimage.io import imread
import matplotlib.pyplot as plt
from data_io import *

four_thirds = 4.0/3.0
pi = np.pi

def volume_abc(r_dil):
    return four_thirds * pi * (r_dil ** 3)

def volume_a(r_den, r_dil):
    h = np.sqrt(( np.square(r_dil) - np.square(r_den) ))
    return four_thirds * pi * (h ** 3)

def volume_bc(r_den, r_dil):
    v_donut = volume_a(r_den, r_dil)
    return ( four_thirds * pi * (r_dil ** 3) ) - v_donut

def volume_c(r_den):
    return four_thirds * pi * (r_den ** 3)

def volume_b(r_den, r_dil):
    return volume_bc(r_den, r_dil) - volume_c(r_den)

def subtract_bg(intden, bg, area):
    return intden - (bg * area)

def mask_droplet(img, x_cen, y_cen, radius):
    y_grid, x_grid = np.ogrid[:img.shape[0], :img.shape[1]]
    drop_mask = np.where((x_grid - x_cen)**2 + (y_grid - y_cen)**2 <= radius**2, 1, 0)
    return drop_mask

def conc_math(r_den, r_dil, intden_bc, intden_abc, conc):
    # does the intensity density math using the donut integral result
    # region a - donut
    # region b - dilute phase within core
    # region c - dense phase wihtin core (spherical)
    # returns cden, cdil
    intden_a = intden_abc - intden_bc
    rho_dil = intden_a / volume_a(r_den, r_dil)
    intden_c = intden_bc - rho_dil * volume_b(r_den, r_dil)
    rho_den = intden_c / volume_c(r_den)
    rho_avg = intden_abc / volume_abc(r_dil)
    conversion = 1 / ((1.0 / conc) * rho_avg)
    
    conc_den = conversion * rho_den
    conc_dil = conversion * rho_dil

    return [conc_den, conc_dil]

def measure_image(log, img, conc):
    rden = log["rden"].to_numpy()
    rdil = log["rdil"].to_numpy()
    xcen = log["xcen"].to_numpy()
    ycen = log["ycen"].to_numpy()

    intden_abc = np.zeros_like(rden)
    intden_bc = np.zeros_like(rden)
    area_abc = np.zeros_like(rden)
    area_bc = np.zeros_like(rden)

    for k, _ in enumerate(rden):
        # iterate over each droplet
        mask_abc = mask_droplet(img, xcen[k], ycen[k], rdil[k])
        mask_bc = mask_droplet(img, xcen[k], ycen[k], rden[k])
        im_abc = img * mask_abc
        im_bc = img * mask_bc
        
        intden_abc[k] = np.sum(im_abc)
        intden_bc[k] = np.sum(im_bc)
        area_abc[k] = np.sum(mask_abc)
        area_bc[k] = np.sum(mask_bc)
        
    cden, cdil = conc_math(rden, rdil, intden_bc, intden_abc, conc)
    
    cap_data = {
        'conc': conc,
        'rden': list(rden),
        'rdil': list(rdil),
        'xcen': list(xcen),
        'ycen': list(ycen),
        'intden_abc': list(intden_abc),
        'intden_bc': list(intden_bc),
        'area_abc': list(area_abc),
        'area_bc': list(area_bc),
        'cden': list(cden),
        'cdil': list(cdil)
    }

    return cap_data

def measure_temperature(log_directory, img_directory, concs_keyval):

    img_paths = [os.path.join(img_directory, img) for img in gather_tif_files(img_directory)]
    imgs = [imread(img) for img in img_paths]
    logs = [pd.read_csv(os.path.join(log_directory, log)) for log in gather_csv_files(log_directory)]
    cap_nums = [extract_cap_number(img_path) for img_path in img_paths]
    
    temp_data = {}
    
    for i, cap_num in enumerate(cap_nums):
        img = imgs[i]
        log = logs[i]
        
        cap_data = measure_image(log, img, concs_keyval[cap_num])
        temp_data[f'cap{cap_num}'] = cap_data
    
    return temp_data



        
            