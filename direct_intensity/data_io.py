import os, sys, re

def gather_json_files(directory):
    if not isinstance(directory, (str, bytes, os.PathLike)):
        raise TypeError("The directory must be a string, bytes, or os.PathLike object.")
    
    if not os.path.isdir(directory):
        raise ValueError("The provided directory path does not exist or is not a directory.")
    
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    
    return json_files

def gather_tif_files(directory):
    tif_files = []
    files = os.listdir(directory)
    for file in files:
        if file.endswith('.tif'):
            tif_files.append(file)
    return sorted(tif_files)

def gather_csv_files(directory):
    csv_files = []
    files = os.listdir(directory)
    for file in files:
        if file.endswith('.csv'):
            csv_files.append(file)
    return sorted(csv_files)

def extract_cap_number(string):
    # extract the digits following the string "cap"
    match = re.search(r'(?i)cap(\d+)', string)
    if match:
        cap_number = int(match.group(1))
        return cap_number
    else:
        return None 
    
def extract_temp_part(string):
    match = re.search(r'(\d+\.?\d*)C', string)
    if match:
        return float(match.group(1))  # Use float to handle decimal numbers
    else:
        return None
    
def list_folders(directory):
    if not isinstance(directory, (str, bytes, os.PathLike)):
        raise TypeError("The directory must be a string, bytes, or os.PathLike object.")
    
    if not os.path.isdir(directory):
        raise ValueError("The provided directory path does not exist or is not a directory.")
    
    folders = [entry.name for entry in os.scandir(directory) if entry.is_dir()]
    return folders

def find_logs_dir(directory):
    if not isinstance(directory, (str, bytes, os.PathLike)):
        raise TypeError("The directory must be a string, bytes, or os.PathLike object.")
    
    if not os.path.isdir(directory):
        raise ValueError("The provided directory path does not exist or is not a directory.")
    
    folders_with_logs = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir() and 'logs' in entry.name:
                folders_with_logs.append(entry.path)
    
    return folders_with_logs

def lollos(x):
    # convert list of lists to list of scalars
    if isinstance(x, list):
        for item in x:
            if isinstance(item, list):
                return [item[0] for item in x]
            else:
                continue
        return x
    else:
        return x