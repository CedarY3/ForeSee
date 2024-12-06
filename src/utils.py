import pickle
import numpy as np
import os

def write_data(data, file_path):
   with open(file_path, 'wb') as f:
       pickle.dump(data, f)

def load_data(file_path):
    with open(file_path, 'rb') as f:
       return pickle.load(f)

def load_single_npy_file(file_path: str, column: int = 0) :
    data_numpy = np.load(file_path)
    return data_numpy[:,column]

def get_npy_files_list(directory):
    return [f for f in os.listdir(directory) if f.endswith('.npy')]
