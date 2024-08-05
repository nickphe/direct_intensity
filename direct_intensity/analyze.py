import os, json
import pandas as pd
import numpy as np
from data_io import *
import matplotlib.pyplot as plt
from config import Config

#SETTINGS
config = Config()
home_dir = config.home_dir
output_dir = config.output_dir
caps = config.caps
concs = config.concs
removed_capillaries = config.removed_capillaries

max_radius = config.max_radius
min_radius = config.min_radius

# create key, value pairs of capillaries and their associated concentrations
considered_caps = [cap_num for cap_num in caps if cap_num not in removed_capillaries]
concs_keyval = dict(zip(caps,concs))

def mkdir(dir):
    # make a directory, if one already exists, skip over it
    try:
        os.mkdir(dir)
    except FileExistsError:
        pass
    
def filter(arr, mask):
    # apply a (0, 1) mask to an array
    b = arr * mask
    return b[b != 0]

mkdir(output_dir)

all_jsons = sorted(gather_json_files(home_dir))

all_cden = {}
all_cdil = {}
all_cden_u = {}
all_cdil_u = {} 
all_N = {}

for i, temp_data_path in enumerate(all_jsons):
    
    # get temperature value of current data, open json file corresponding to temperature
    temp = extract_temp_part(temp_data_path)
    f = open(temp_data_path, 'r')
    temp_data = json.load(f)
    
    # make temperature directory
    temp_output_dir = os.path.join(output_dir, f'{temp}C')
    mkdir(temp_output_dir)
    
    cdens = {}
    cdils = {}
    cdens_u = {}
    cdils_u = {}
    Ns = {}
    
    # for each cap image, filter the data, save it in accessible format
    for cap_num in caps:
        
        cap_output_dir = os.path.join(temp_output_dir, f'cap{cap_num}, {concs_keyval[cap_num]} uM')
        mkdir(cap_output_dir)
        try:
            cap_data = temp_data[f'cap{cap_num}']
        except:
            print(f'Capillary {cap_num} does not exist at temperature: {temp}C')
            continue
        
        # save all capillary output data to corresponding capillary/temperature directory
        df = pd.DataFrame(cap_data)
        df.to_csv(os.path.join(cap_output_dir, f'{temp}C_cap{cap_num}_droplet_data.csv'))

        conc = concs_keyval[cap_num]
        cden = np.array(cap_data['cden'])
        cdil = np.array(cap_data['cdil'])
        rden = np.array(cap_data['rden'])
        rdil = np.array(cap_data['rdil'])
        xcen = np.array(cap_data['xcen'])
        ycen = np.array(cap_data['ycen'])
        intden_abc = np.array(cap_data['intden_abc'])
        intden_bc = np.array(cap_data['intden_bc'])
        area_abc = np.array(cap_data['area_abc'])
        area_bc = np.array(cap_data['area_bc'])
    
        remove_too_large = np.where(rdil < max_radius, 1, 0)
        remove_too_small = np.where(rdil > min_radius, 1, 0)
        makes_no_sense = np.where(cdil > conc, 0, 1)
        extra_peculiar = np.where(rden > rdil, 0, 1)
        too_small_to_be_measured = np.where(rden < 5, 0, 1)
        outta_here = remove_too_large * remove_too_small * makes_no_sense * extra_peculiar * too_small_to_be_measured
        
        f_cden = filter(cden, outta_here)
        f_cdil = filter(cdil, outta_here)
        f_rden = filter(rden, outta_here)
        f_rdil = filter(rdil, outta_here)
        f_xcen = filter(xcen, outta_here)
        f_ycen = filter(ycen, outta_here)
        f_intden_abc = filter(intden_abc, outta_here)
        f_intden_bc = filter(intden_bc, outta_here)
        f_area_abc = filter(area_abc, outta_here)
        f_area_bc = filter(area_bc, outta_here)
        
        d = {
        'rden': list(f_rden),
        'rdil': list(f_rdil),
        'xcen': list(f_xcen),
        'ycen': list(f_ycen),
        'intden_abc': list(f_intden_abc),
        'intden_bc': list(f_intden_bc),
        'area_abc': list(f_area_abc),
        'area_bc': list(f_area_bc),
        'cden': list(f_cden),
        'cdil': list(f_cdil)
        }   
        df = pd.DataFrame(data = d)
        df.to_csv(os.path.join(cap_output_dir, f'{temp}C_cap{cap_num}_filtered_droplet_data.csv'))
        
        N =  len(cden)
        mean_cden = [np.mean(f_cden)]
        std_cden = [np.std(f_cden)]
        mean_cdil = [np.mean(f_cdil)]
        std_cdil = np.std(f_cdil)
        mean_rden = np.mean(f_rden)
        std_rden = np.std(f_rden)
        mean_rdil = np.mean(f_rdil)
        std_rdil = np.std(f_rdil)
        
        d = {
            'N': N,
            'mean cden': mean_cden,
            'cden stdev':std_cden ,
            'mean cdil': mean_cdil,
            'cdil stdev': std_cdil,
            'mean rden': mean_rden,
            'rden stdev': std_rden,
            'mean rdil': mean_rdil,
            'rdil stdev': std_rdil
        }
        df = pd.DataFrame(data = d)
        df.to_csv(os.path.join(cap_output_dir, f'{temp}C_cap{cap_num}_stats.csv'))
        
        cdens[cap_num] = mean_cden
        cdils[cap_num] = mean_cdil
        cdens_u[cap_num] = std_cden
        cdils_u[cap_num] = std_cdil
        Ns[cap_num] = N
    
    all_cden[temp] = cdens
    all_cdil[temp] = cdils
    all_cden_u[temp] = cdens_u
    all_cdil_u[temp] = cdils_u
    all_N[temp] = Ns 

temps = [extract_temp_part(f) for f in sorted(list_folders(home_dir))]
temps = sorted(temps)

# save PD data in convenient format
pd_data = pd.DataFrame()
conc_li = []
cden_li = []
cden_u_li = []
cdil_li = []
cdil_u_li = []
N_li = []
temp_li = []

for temp in temps:
    cdens = all_cden[temp]
    cdils = all_cdil[temp]
    cdens_u = all_cden_u[temp]
    cdils_u = all_cdil_u[temp]
    Ns = all_N[temp]
    
    print(cdens)
    
    for i, cap_num in enumerate(considered_caps):
        conc = concs_keyval[cap_num]
        print(conc)
        try:
            cden = cdens[cap_num]
            cdil = cdils[cap_num]
            cden_u = cdens_u[cap_num]
            cdil_u = cdils_u[cap_num]
            N = Ns[cap_num]
        except:
            print(f'capillary {cap_num} missing from temp {temp}')
            continue
        cindex = int(concs_keyval[cap_num]/np.max(concs) * 100) 
        print(f'cindex = {cindex}')
        
        conc_li.append(conc)
        cden_li.append(cden)
        cden_u_li.append(cden_u)
        cdil_li.append(cdil)
        cdil_u_li.append(cdil_u)
        N_li.append(N)
        temp_li.append(temp)
        
pd_data['cinit'] = lollos(conc_li)
pd_data['temp'] = lollos(temp_li)
pd_data['cden_mean'] = lollos(cden_li)
pd_data['cden_std'] = lollos(cden_u_li)
pd_data['cdil_mean'] = lollos(cdil_li)
pd_data['cdil_std'] = lollos(cdil_u_li)
pd_data['N'] = lollos(N_li)

pd_data.to_csv(os.path.join(output_dir, 'pd_data.csv'))




# FIGURES


fig, ax = plt.subplots(dpi = 400)
ax.set_xlabel("$\\rho/\\rho_{\mathrm{avg}}$ ($\\mu$M)")
ax.set_ylabel("Temperature ($^\\circ$C)")

colors = plt.cm.gnuplot2(np.linspace(0,1,110))

for temp in temps:
    cdens = all_cden[temp]
    cdils = all_cdil[temp]
    cdens_u = all_cden_u[temp]
    cdils_u = all_cdil_u[temp]
    Ns = all_N[temp]
    
    print(cdens)
    
    for i, cap_num in enumerate(considered_caps):
        conc = concs_keyval[cap_num]
        print(conc)
        try:
            cden = cdens[cap_num]
            cdil = cdils[cap_num]
            cden_u = cdens_u[cap_num]
            cdil_u = cdils_u[cap_num]
            N = Ns[cap_num]
        except:
            print(f'capillary {cap_num} missing from temp {temp}')
            continue
        cindex = int(concs_keyval[cap_num]/np.max(concs) * 100) 
        print(f'cindex = {cindex}')
        
        if temp == temps[0]:
            ax.errorbar(np.array(cden)/conc, temp, xerr = cden_u/np.sqrt(N)/conc,  marker = "o", linestyle = "", color = colors[cindex], capsize = 5, label = f'{conc} $\\mu$M')
        else:
            ax.errorbar(np.array(cden)/conc, temp, xerr = cden_u/np.sqrt(N)/conc,  marker = "o", linestyle = "", color = colors[cindex], capsize = 5)
        ax.errorbar(np.array(cdil)/conc, temp, xerr = cdil_u/np.sqrt(N)/conc, marker = "o", linestyle = "", color = colors[cindex], capsize = 5)
    
ax.legend(fontsize = 'small')
ax.minorticks_on()
plt.savefig(os.path.join(output_dir, '2d_pd.jpg'))


# 3d figure

fig = plt.figure(dpi = 400)
ax = fig.add_subplot(projection='3d')

colors = plt.cm.gnuplot2(np.linspace(0,1,110))

for temp in temps:
    cdens = all_cden[temp]
    cdils = all_cdil[temp]
    cdens_u = all_cden_u[temp]
    cdils_u = all_cdil_u[temp]
    Ns = all_N[temp]
    
    print(cdens)
    
    for i, cap_num in enumerate(considered_caps):
        conc = concs_keyval[cap_num]
        try:
            cden = cdens[cap_num]
            cdil = cdils[cap_num]
            cden_u = cdens_u[cap_num]
            cdil_u = cdils_u[cap_num]
            N = Ns[cap_num]
        except:
            print(f'capillary {cap_num} missing from temp {temp}')
            continue
        cindex = int(concs_keyval[cap_num]/np.max(concs) * 100) 
        print(f'cindex = {cindex}')
        
        if temp == temps[0]:
            ax.scatter(cden, conc * np.ones_like(cden),temp,  marker = "o", linestyle = "", color = colors[cindex], label = f'{conc} $\\mu$M')
        else:
            ax.scatter(cden, conc * np.ones_like(cden), temp,  marker = "o", linestyle = "", color = colors[cindex])
        ax.scatter(cdil, conc * np.ones_like(cdil), temp, marker = "o", linestyle = "", color = colors[cindex])

ax.minorticks_on()
ax.set_xlabel('Binodal Concentrations ($\\mu$M)')
ax.set_ylabel('Initial Concentrations ($\\mu$M)')
ax.set_zlabel('Temperature ($^\\circ$C)')
plt.savefig(os.path.join(output_dir, '3d_pd.jpg'))

