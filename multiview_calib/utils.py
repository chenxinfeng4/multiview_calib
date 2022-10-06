#----------------------------------------------------------------------------
# Created By  : Leonardo Citraro leonardo.citraro@epfl.ch
# Date: 2020
# --------------------------------------------------------------------------
import os
import sys
import json
import re
import os
import ast
import glob
import shutil
import pickle
import logging
import numpy as np

__all__ = ["json_read", "json_write", "pickle_read", "pickle_write", 
           "mkdir", "rmdir", "sort_nicely", "find_files", "find_images", 
           "invert_Rt", "rgb2gray", "draw_points", "draw_rectangles", 
           "dict_keys_to_string", "dict_keys_from_literal_string", "indexes",
           "draw_points", "draw_rectangles"]

colors = [[1,0,0], [0,1,0], [0,0,1], 
           [0,0,0], [1,1,1], [1,1,0],
           [1,0,1], [0,1,1]]+[np.random.rand(3).tolist() for _ in range(100)]

def json_read(filename):
    try:
        with open(os.path.abspath(filename)) as f:    
            data = json.load(f)
        return data
    except:
        raise ValueError("Unable to read JSON {}".format(filename))
        
def json_write(filename, data):
    try:
        directory = os.path.dirname(os.path.abspath(filename))
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.abspath(filename), 'w') as f:
            json.dump(data, f, indent=2)
    except:
        raise ValueError("Unable to write JSON {}".format(filename))   
        
def pickle_read(filename):
    with open(filename, "rb") as f:    
        data = pickle.load(f)
    return data

def pickle_write(filename, data):
    directory = os.path.dirname(os.path.abspath(filename))
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filename, 'wb') as f:
        pickle.dump(data, f)        

def mkdir(directory):
    directory = os.path.abspath(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def rmdir(directory):
    directory = os.path.abspath(directory)
    if os.path.exists(directory): 
        shutil.rmtree(directory)        

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key=alphanum_key)

def find_files(file_or_folder, hint=None, recursive=False):
    # make sure to use ** in file_or_folder when using recusive
    # ie find_files("folder/**", "*.json", recursive=True)
    import os
    import glob
    if hint is not None:
        file_or_folder = os.path.join(file_or_folder, hint)
    filenames = [f for f in glob.glob(file_or_folder, recursive=recursive)]
    filenames = sort_nicely(filenames)    
    filename_files = []
    for filename in filenames:
        if os.path.isfile(filename):
            filename_files.append(filename)                 
    return filename_files

def find_images(file_or_folder, hint=None):  
    filenames = find_files(file_or_folder, hint)
    filename_images = []
    for filename in filenames:
        _, extension = os.path.splitext(filename)
        if extension.lower() in [".jpg",".jpeg",".bmp",".tiff",".png",".gif"]:
            filename_images.append(filename)                 
    return filename_images  

def dict_keys_to_string(d):
    return {str(key):value for key,value in d.items()}

def dict_keys_from_literal_string(d):
    new_d = {}
    for key,value in d.items():
        if isinstance(key, str):
            try:
                new_key = ast.literal_eval(key)
            except:
                new_key = key
        else:
            new_key = key
        new_d[new_key] = value
    return new_d

def rgb2gray(image):
    dtype = image.dtype
    gray = np.dot(image[...,:3], [0.299, 0.587, 0.114])
    return gray.astype(dtype)

def invert_Rt(R, t):
    Ri = R.T
    ti = np.dot(-Ri, t)
    return Ri, ti

def indexes(_list, value):
    return [i for i,x in enumerate(_list) if x==value]

def config_logger(log_file=None):
    """
    Basic configuration of the logging system. Support logging to a file.
    Log messages can be submitted from any script.
    config_logger(.) is called once from the main script.
    
    Example
    -------
    import logging
    logger = logging.getLogger(__name__)
    utils.config_logger("main.log")
    logger.info("this is a log.")    
    """

    class MyFormatter(logging.Formatter):

        info_format = "\x1b[32;1m%(asctime)s [%(name)s]\x1b[0m %(message)s"
        error_format = "\x1b[31;1m%(asctime)s [%(name)s] [%(levelname)s]\x1b[0m %(message)s"

        def format(self, record):

            if record.levelno > logging.INFO:
                self._style._fmt = self.error_format
            else:
                self._style._fmt = self.info_format

            return super(MyFormatter, self).format(record)

    rootLogger = logging.getLogger()

    if rootLogger.hasHandlers():
        rootLogger.handlers.clear()

    if log_file is not None:
        fileHandler = logging.FileHandler(log_file)
        fileFormatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s]> %(message)s")
        fileHandler.setFormatter(fileFormatter)
        rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleFormatter = MyFormatter()
    consoleHandler.setFormatter(consoleFormatter)
    rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(logging.INFO)
    
class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        temp_linebuf = self.linebuf + buf
        self.linebuf = ''
        for line in temp_linebuf.splitlines(True):
            # From the io.TextIOWrapper docs:
            #   On output, if newline is None, any '\n' characters written
            #   are translated to the system default line separator.
            # By default sys.stdout.write() expects '\n' newlines and then
            # translates them so this is still cross platform.
            if line[-1] == '\n':
                self.logger.log(self.log_level, line.rstrip())
            else:
                self.linebuf += line

    def flush(self):
        if self.linebuf != '':
            self.logger.log(self.log_level, self.linebuf.rstrip())
        self.linebuf = ''

def draw_rectangles(image, centers, size, color='r', thickness=3): 
    """ Draws rectangles on the image
    """ 
    _image = image.copy()
    if color=='r':
        color = [255,0,0]
    elif color=='g':
        color = [0,255,0]
    elif color=='b':
        color = [0,0,255]
    elif color=='w':
        color = [255,255,255]
    elif color=='k':
        color = [0,0,0]
        
    for i, (x,y) in enumerate(np.int_(centers)):
        pt1 = (x-size[1]//2, y-size[0]//2)
        pt2 = (x+size[1]//2, y+size[0]//2)
        _image = cv2.rectangle(_image, pt1, pt2, color=color, thickness=thickness)
    return _image

def draw_points(image, centers, radius, color='r'): 
    """ Draws filled point on the image
    """
    _image = image.copy()        
    if color=='r':
        color = [255,0,0]
    elif color=='g':
        color = [0,255,0]
    elif color=='b':
        color = [0,0,255]
    elif color=='w':
        color = [255,255,255]
    elif color=='k':
        color = [0,0,0]
    
    for point in centers:
        _image = cv2.circle(_image, tuple(point.astype(np.int)), radius, color=color, thickness=-1)
    return _image