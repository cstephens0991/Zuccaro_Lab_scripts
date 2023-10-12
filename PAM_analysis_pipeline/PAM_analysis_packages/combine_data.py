import pandas as pd
import glob
import re
import numpy as np

Plant_area_files_list = glob.glob("./Plant_area_data/*_threshold_image.csv")
total_data = pd.DataFrame([], columns=["Plate", "Count", "Total Area", "Average Size", "%Area", "Mean"])

for area_file in Plant_area_files_list:
    plate_name = area_file.split("./Plant_area_data\\")[1]
    plate_name = plate_name.split("_threshold_image.csv")[0]
    plate_data = pd.read_csv(area_file)
    if plate_data.shape[0] != 24:
        print(f"{plate_name} length is {plate_data.shape[0]}")
    plate_data["Plate"] = plate_name
    plate_data['Well'] = np.arange(1, (len(plate_data)+1)).astype(int)
    plate_data = plate_data.drop(columns="Slice")
    total_data = pd.concat([total_data, plate_data], axis=0)

fvfm_data = pd.read_csv("./output/FvFm_output.csv")
fvfm_data.head()
final_data = total_data.merge(fvfm_data, how="inner", on=["Plate", "Well"])
final_data = final_data.drop(columns=["Count", "Average Size", "%Area", "Mean", "Unnamed: 0"])
# Combine ImageJ area score and FvFm score into a single value
final_data["Area_FvFm"] = final_data["Total Area"] * final_data["FvFm"]

final_data.to_csv("./output/Combined_output.csv")