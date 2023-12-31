## get_fvfm_v1.0

# This script is used to carry out the first stage of the PAM data analysis pipeline

# If using this script **it is important to acknowledge the code contributors**:
# - pim2tiff.exe was developed and provided by Oliver Meyerhoff of Walz (supplier of the PAM imager)
# - The Multi2singleframes.extract_frame script is an edited version of that developed by Dominik Schneider et al. and published here (https://doi.org/10.1186/s13007-019-0546-1). See also GitHub for source scripts (https://github.com/CougPhenomics/ImagingPAMProcessing).
# - The plantcv_current.yml environment file was also sourced from scripts written by Schneider et al.
# - The FvFm calculations were carried out using scripts generated by PlantCV. See https://plantcv.readthedocs.io/en/stable/photosynthesis_analyze_fvfm/ for tutorial and GitHub (https://github.com/danforthcenter/plantcv/blob/main/plantcv/plantcv/photosynthesis/analyze_fvfm.py) for source scripts.

###
# **Note:** This script can only be run using the "plantcv" environment, which contains the required Plantcv packages (as well as Python and subpackages). This can potentially be changed later, by extracting the source codes for setting the threshold...

# Before running locally, it is necessary to generate a conda environment, using the plantcv_current.yml file.

### Import all required scripts and functions:
import re
import os
import glob
import shutil
import pandas as pd
import numpy as np
import math

# Required for setting threshold images (and subsequent cleaning)
from plantcv import plantcv as pcv
from skimage import filters

# Edited FvFm value extraction script
from scripts import Analyse_FvFm_new

# Convert tiff stack to individual files
from scripts import Multi2Singleframes
# Run executable
import subprocess
# Cut up tiff images
from PIL import Image

# Required for image export in ProcessImages.py script (not yet used here...)
import cv2 as cv2

# Get list of files to analyse
xpim_files = glob.glob("./input/xpim_files/*.xpim")
file_list = []
for file in xpim_files:
    bn = os.path.basename(file)
    bn = bn.strip(".xpim")
    file_list.append(bn)


# Convert xpim files to tif files. This utilises the "pim2tif.exe" executable.
subprocess.check_call(["./scripts/pim2tiff.exe", "./input/xpim_files"])

# Move tif files to the input/tif_files folder
tif_files = glob.glob("./input/xpim_files/*.tif")
for file in tif_files:
    basename = os.path.basename(file)
    destination = "./input/tiff_files/" + basename
    shutil.move(file, destination)

# Separate the tif stacks in to individual images
tiff_frames = "./input/tiff_files/tiff_frames"

# Delete any tiff_frames file that already exists and replace with an empty one
if os.path.exists(tiff_frames):
    shutil.rmtree(tiff_frames)
os.makedirs(tiff_frames) 

for tiff_stack in glob.glob("./input/tiff_files/*.tif"):
    Multi2Singleframes.extract_frames(tiff_stack, "./input/tiff_files/tiff_frames")

# Preset list for well positions.
# Note: Please check at the end of the data extraction process, that all the leaf area (and none from neighbouring wells) has been successfully captured.
Well_1 = (100,130,170,200)
Well_2 = (170,130,240,200)
Well_3 = (240,130,310,200)
Well_4 = (310,130,380,200)
Well_5 = (380,130,450,200)
Well_6 = (450,130,520,200)
Well_7 = (100,200,170,270)
Well_8 = (170,200,240,270)
Well_10 = (310,200,380,270)
Well_11 = (380,200,450,270)
Well_12 = (450,200,520,270)
Well_13 = (100,270,170,340)
Well_14 = (170,270,240,340)
Well_9 = (240,200,310,270)
Well_15 = (240,270,310,340)
Well_16 = (310,270,380,340)
Well_17 = (380,270,450,340)
Well_18 = (450,270,520,340)
Well_19 = (100,340,170,410)
Well_20 = (170,340,240,410)
Well_21 = (240,340,310,410)
Well_22 = (310,340,380,410)
Well_23 = (380,340,450,410)
Well_24 = (450,340,520,410)

# Delete any previously existing debug folder and replace with empty directories
cropped_plate_output = "./debug/cropped_images"
if os.path.exists(cropped_plate_output):
    shutil.rmtree(cropped_plate_output)
os.makedirs(cropped_plate_output) 
# Make output directories for the cropped images
# Individual directories are generated for ease of deletion later.
os.makedirs(f"{cropped_plate_output}/fmin")
os.makedirs(f"{cropped_plate_output}/fmax")
os.makedirs(f"{cropped_plate_output}/fdark")
os.makedirs(f"{cropped_plate_output}/threshold")

# Create output pandas df
output_df = pd.DataFrame([], columns=["Plate", "Well", "FvFm"])
# For each file to analyse, generate and export the "fmax" image. This can be used for later debugging
# Count for the number of plate image files analysed
file_count = 0
for image_file in file_list:
    print(f"Analysing {image_file}")
    file_count = file_count + 1
        
    # Create contrast image and save to output/threshold_output folder
    fmin_plate, path, filename = pcv.readimage(f"./input/tiff_files/tiff_frames/{image_file}-1.tif", mode="native")
    fmax_plate, path, filename = pcv.readimage(f"./input/tiff_files/tiff_frames/{image_file}-2.tif", mode="native")
    fdark_plate, path, filename = pcv.readimage(f"./input/tiff_files/tiff_frames/{image_file}-3.tif", mode="native")
    yen_threshold = filters.threshold_yen(image=fmax_plate)
    threshold_image = pcv.threshold.binary(gray_img=fmax_plate, threshold=yen_threshold, max_value=255, object_type='light')
    threshold_image = pcv.fill(threshold_image, size=5)
    cv2.imwrite(f"./output/threshold_output/{image_file}_threshold_image.tif", threshold_image)

    # Create images for each well
    for i in range(1,25):
        
        # For each plate image, the image is opened, cropped and the cropped image is saved
        with Image.open(f"./input/tiff_files/tiff_frames/{image_file}-1.tif") as plate_fmin:
            cropped_fmin = plate_fmin.crop(locals()["Well_"+str(i)])
            cropped_fmin.save(f"./debug/cropped_images/fmin/{image_file}_fmin_Well-{i}.tif", format=None)
            
        with Image.open(f"./input/tiff_files/tiff_frames/{image_file}-2.tif") as plate_fmax:
            cropped_fmax = plate_fmax.crop(locals()["Well_"+str(i)])
            cropped_fmax.save(f"./debug/cropped_images/fmax/{image_file}_fmax_Well-{i}.tif", format=None)
            
        with Image.open(f"./input/tiff_files/tiff_frames/{image_file}-3.tif") as plate_fdark:
            cropped_fdark = plate_fdark.crop(locals()["Well_"+str(i)])
            cropped_fdark.save(f"./debug/cropped_images/fdark/{image_file}_fdark_Well-{i}.tif", format=None)
        
        # Read back in using pcv functions (reads in images as numpy arrays)
        fmin, _, _ = pcv.readimage(f"./debug/cropped_images/fmin/{image_file}_fmin_Well-{i}.tif", mode="native")
        fmax, _, _ = pcv.readimage(f"./debug/cropped_images/fmax/{image_file}_fmax_Well-{i}.tif", mode="native")
        fdark, _, _ = pcv.readimage(f"./debug/cropped_images/fdark/{image_file}_fdark_Well-{i}.tif", mode="native")

        #Return threshold value based on Yen’s method.
        yen_threshold = filters.threshold_yen(image=fmax)
        # Use the threshold value to filter out highlighted plate areas
        threshold_image = pcv.threshold.binary(gray_img=fmax, threshold=yen_threshold, max_value=255, object_type='light')
        threshold_image = pcv.fill(threshold_image, size=5)
        # Carry out FvFm calculation
        part_Fv = Analyse_FvFm_new.analyze_fvfm(fdark=fdark, fmin=fmin, fmax=fmax, mask=threshold_image, bins=256, label="fluor")
        if math.isnan(part_Fv):
            print(f"fvfm for {image_file}, well {i} is nan!")
        df = pd.DataFrame([[image_file, i, part_Fv]], columns = ["Plate", "Well", "FvFm"])
        output_df = pd.concat([output_df, df])
        # part_Fv, part_hist_fvfm = pcv.photosynthesis.analyze_fvfm(fdark=fdark, fmin=fmin, fmax=fmax, mask=threshold_image, bins=256, label="fluor")
        
        ################## Edit/remove this section? Introduction of bias!! #############################
        # To remove areas of wells still included after thresholding, pcv.fill removes objects that are less than specified size"
        # However, we need different levels of filtering for different wells. To rigorous filtering for some wells will remove plants from others!
        # pixel_count = cv2.countNonZero(threshold_image)
        # print(pixel_count)
        # if pixel_count > 500:
        #     threshold_image = pcv.fill(threshold_image, size=(pixel_count/5))
        #     threshold_image = pcv.erode(threshold_image,2,1)
        #     threshold_image = pcv.fill(threshold_image, pixel_count/10)
        # else: threshold_image = pcv.fill(threshold_image, size=1)
        ###################################################################################################

        # Export threshold images to debug folder
        cv2.imwrite(f"./debug/cropped_images/threshold/{image_file}_threshold_Well-{i}.tif", threshold_image)

output_df = output_df.reset_index().drop(columns="index")
output_df.to_csv("./output/FvFm_output.csv")

print(f"End of script. Number of files analysed: {file_count}")

# Finally, remove unnecessary directories
shutil.rmtree(f"{cropped_plate_output}/fmin", ignore_errors=True)
shutil.rmtree(f"{cropped_plate_output}/fdark", ignore_errors=True)
shutil.rmtree(tiff_frames, ignore_errors=True)
# fmax and threshold will be kept for debugging purposes.