import os
from os import listdir
from os.path import isfile, join
import json
import pickle


class FileService():

    base_dir: str

    def __init__(self):

        self.base_dir = os.path.dirname(os.path.abspath(__file__)) + '/..'

    def get_files_in_folder(self, path, is_path_relative=True):
        '''
            Loads all files in the given relative folder

            Args:
                path: Path to directory
                is_path_relative: If true, path ust be relative to application base directoys
        '''

        files = []
        fullpath = path + '/'
        if is_path_relative:
            fullpath = self.base_dir + path + '/'
        for file in listdir(fullpath):
            file_path = fullpath + file
            if isfile(file_path):
                files.append(file_path)
        return files

    def load_json(self, file_path, is_path_relative=True):

        fullpath = file_path 
        if is_path_relative:
            fullpath = self.base_dir + file_path 

        with open(fullpath) as f:
            json_obj = json.load(f)
         
        f.close()
        return json_obj

    def save_json(self, file_path, data, is_path_relative=True):

        fullpath = file_path 
        if is_path_relative:
            fullpath = self.base_dir + file_path

        with open(fullpath, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
        f.close()

    def save_string(self, file_path, data, is_path_relative=True):

        fullpath = file_path 
        if is_path_relative:
            fullpath = self.base_dir + file_path

        with open(fullpath, 'w') as f:
            f.write(data)
        f.close()

    def load_string(self, file_path, is_path_relative=True):
        
        fullpath = file_path 
        if is_path_relative:
            fullpath = self.base_dir + file_path 
        
        with open(fullpath, "rb") as f:
            data = f.read()
        f.close()
        return data


    def save_data(self, file_path, data, is_path_relative=True):
        
        fullpath = file_path 
        if is_path_relative:
            fullpath = self.base_dir + file_path 
        
        with open(fullpath, "wb") as f:
            pickle.dump(data, f)
        f.close()

    def load_data(self, file_path, is_path_relative=True):
        
        fullpath = file_path 
        if is_path_relative:
            fullpath = self.base_dir + file_path 
        
        with open(fullpath, "rb") as f:
            data = pickle.load( f)
        f.close()
        return data


        
        
        
