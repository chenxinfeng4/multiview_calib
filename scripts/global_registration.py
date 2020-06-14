import numpy as np
import argparse
import matplotlib
import imageio
import cv2
import os
import warnings
warnings.filterwarnings("ignore")

matplotlib.use("Agg")

from multiview_calib import utils
from multiview_calib.calibration import global_registration, visualise_global_registration

def main(ba_poses='ba_poses.json',
         ba_points='ba_points.json',
         landmarks_global='landmarks_global',
         dump_images=True,
         filenames="filenames.json",
         output_path="output/global_registration"):
    
    ba_poses = utils.json_read(ba_poses)
    ba_points = utils.json_read(ba_points)
    landmarks_global = utils.json_read(landmarks_global)
    
    global_poses = global_registration(ba_poses, ba_points, landmarks_global)  
    
    if dump_images:
        filenames = utils.json_read(filenames)
        visualise_global_registration(global_poses, landmarks_global, ba_poses, ba_points, 
                                      filenames, output_path="output/global_registration")
            
    utils.json_write("global_poses.json", global_poses)
    
if __name__ == "__main__":

    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')    

    parser = argparse.ArgumentParser()   
    parser.add_argument("--ba_poses", "-ps", type=str, required=True, default="ba_poses.json",
                        help='JSON file containing the optimized poses')
    parser.add_argument("--ba_points", "-po", type=str, required=True, default="ba_points.json",
                        help='JSON file containing the optimized 3d points')
    parser.add_argument("--landmarks_global", "-l", type=str, required=True, default="landmarks_global.json",
                        help='JSON file containing the corresponding global landmarks') 

    parser.add_argument("--dump_images", "-d", default=False, const=True, action='store_const',
                        help='Saves images for visualisation')   
    parser.add_argument("--filenames", "-f", type=str, required=False, default="filenames.json",
                        help='JSON file containing one filename of an image for each view')    
    
    args = parser.parse_args()

    main(**vars(args))

# python global_registration.py -ps ba_poses.json -po ba_points.json -l landmarks_global.json -f filenames.json --dump_images