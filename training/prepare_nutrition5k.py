"""
Script to help prepare Nutrition5k dataset for YOLOv8 segmentation training.
NOTE: Nutrition5k dataset requires manual download due to license/size.
This script assumes you have downloaded the dataset and placed it in 'datasets/nutrition5k_raw'.

It converts the Nutrition5k metadata (dish_ids, ingredients, mass) and RGB-D images
into YOLOv8 segmentation format.
"""

import os
import json
import shutil
import numpy as np
import cv2
from pathlib import Path
from tqdm import tqdm
import pandas as pd

# Configuration
RAW_DIR = Path("datasets/nutrition5k_raw")
OUTPUT_DIR = Path("datasets/nutrition5k-yolo")

def check_raw_data():
    if not RAW_DIR.exists():
        print(f"❌ Raw dataset not found at {RAW_DIR}")
        print("Please download Nutrition5k dataset manually from: https://github.com/google-research-datasets/nutrition5k")
        print(f"And extract it to {RAW_DIR.absolute()}")
        return False
    return True

def convert_to_yolo_seg():
    """
    Converts Nutrition5k data to YOLO segmentation format.
    Requires:
    - RGB images
    - Masks (if provided, otherwise we might need to generate them from depth or use bounding boxes)
    - Metadata for class labels
    """
    print("Converting Nutrition5k to YOLOv8 segmentation format...")
    
    # Create YOLO directory structure
    (OUTPUT_DIR / "train" / "images").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "train" / "labels").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "val" / "images").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "val" / "labels").mkdir(parents=True, exist_ok=True)
    
    # Load metadata
    metadata_path = RAW_DIR / "metadata.csv" # Hypothetical path, adjust based on actual dataset structure
    if not metadata_path.exists():
        print(f"Metadata file not found at {metadata_path}")
        return

    # This is a placeholder for the complex logic needed to parse Nutrition5k
    # Nutrition5k provides: dish_id, total_calories, total_mass, ingredients list
    # It also provides overhead RGB and Depth images.
    
    # Real implementation would:
    # 1. Iterate through each dish_id
    # 2. Load RGB image
    # 3. Load overhead masks (if available) or generate from depth
    # 4. Map ingredients to class IDs
    # 5. Write YOLO label file (class_id x1 y1 ... xn yn) for segmentation
    
    print("⚠️ This script is a template. You need to download the dataset first.")
    print("Once downloaded, this script would iterate through 'dish_metadata' and convert masks to polygons.")
    
    # Example of writing a dummy config file
    data_yaml = """
path: ../datasets/nutrition5k-yolo
train: train/images
val: val/images

nc: 100 # Number of classes (approx)
names: ['rice', 'chicken', 'broccoli', ...] # List of ingredient names
    """
    
    with open(OUTPUT_DIR / "data.yaml", "w") as f:
        f.write(data_yaml)
        
    print(f"Created template configuration at {OUTPUT_DIR / 'data.yaml'}")

if __name__ == "__main__":
    if check_raw_data():
        convert_to_yolo_seg()
    else:
        # Create a dummy structure so the user sees where to put files
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        print("Created placeholder directory. Please populate it with dataset files.")
