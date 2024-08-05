import os, json
from data_io import *
from direct_intensity import * 
from config import Config

#SETTINGS
config = Config()
home_dir = config.home_dir
output_dir = config.output_dir
caps = config.caps
concs = config.concs
removed_capillaries = config.removed_capillaries

considered_caps = [cap_num for cap_num in caps if cap_num not in Config.removed_capillaries]
concs_keyval = dict(zip(caps,concs))

log_directories = [find_logs_dir(os.path.join(home_dir, temp_folder))[0] for temp_folder in list_folders(home_dir)]
img_directories = [os.path.join(home_dir, temp_folder) for temp_folder in list_folders(home_dir)]

for i, log_directory in enumerate(log_directories):
    
    img_directory = img_directories[i]
    temp = extract_temp_part(img_directory)
    temp_data = measure_temperature(log_directory, img_directory, concs_keyval)
    # save temp data to json file inside its folder
    with open(os.path.join(img_directory, f'{temp}C_data.json'), 'w') as f:
        json.dump(temp_data,f)
