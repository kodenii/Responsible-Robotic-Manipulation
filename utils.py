import logging
import os
import time

def read_txt(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = f.read()
    return data

def create_time_based_folder(base_directory):
    current_time = time.strftime('%Y-%m-%d-%H-%M-%S')
    
    folder_name = f"{current_time}"
    folder_path = os.path.join(base_directory, folder_name)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder: {folder_path}")
    else:
        print(f"Existed: {folder_path}")
    
    return folder_path

def setup_logger(log_folder, log_filename = 'mental.log', log_level=logging.INFO):
    log_path = os.path.join(log_folder, log_filename)

    logger = logging.getLogger()
    logging.basicConfig()
    logger.setLevel(log_level)

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger