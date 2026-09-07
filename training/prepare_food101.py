"""
Script to prepare Food-101 dataset for YOLOv8 training.
Downloads the dataset, converts annotations (if any) or structure to YOLO format.
Note: Food-101 is a classification dataset. For detection, we might need to synthesize bounding boxes
or use it purely for classification pre-training. 
However, for this pipeline, we will assume we want to use it to train a classifier head 
or use a subset that has been annotated for detection if available, 
but standard Food-101 is classification only.

To make this useful for YOLOv8-seg, we ideally need segmentation masks.
Since Food-101 is classification only, we will set this up for *classification* training
which is still useful for the 'FoodClassifier' component of Cal-AI.

For detection/segmentation, we really rely on Nutrition5k or UECFood which have more spatial info.
"""

import os
import shutil
import tarfile
import urllib.request
from pathlib import Path
import random
from tqdm import tqdm

# Configuration
DATASET_URL = "http://data.vision.ee.ethz.ch/cvl/food-101.tar.gz"
DATA_DIR = Path("datasets/food-101")
YOLO_DIR = Path("datasets/food-101-yolo")

def download_and_extract():
    if DATA_DIR.exists():
        print(f"Dataset found at {DATA_DIR}, skipping download.")
        return

    print(f"Downloading Food-101 from {DATASET_URL}...")
    DATA_DIR.parent.mkdir(parents=True, exist_ok=True)
    tar_path = DATA_DIR.parent / "food-101.tar.gz"
    
    # Download with progress bar
    with tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=tar_path.name) as t:
        def reporthook(b=1, bsize=1, tsize=None):
            t.total = tsize
            t.update(b * bsize - t.n)
        urllib.request.urlretrieve(DATASET_URL, tar_path, reporthook=reporthook)

    print("Extracting...")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=DATA_DIR.parent)
    
    # Cleanup
    os.remove(tar_path)
    print("Download and extraction complete.")

def prepare_for_yolo_classification():
    """
    Rearranges Food-101 into YOLO classification format:
    dataset/
        train/
            class1/
            class2/
        val/
            class1/
            class2/
    """
    print("Preparing dataset for YOLOv8 classification...")
    
    if YOLO_DIR.exists():
        shutil.rmtree(YOLO_DIR)
    
    images_dir = DATA_DIR / "food-101" / "images"
    meta_dir = DATA_DIR / "food-101" / "meta"
    
    # Create directories
    (YOLO_DIR / "train").mkdir(parents=True, exist_ok=True)
    (YOLO_DIR / "val").mkdir(parents=True, exist_ok=True)
    
    # Read split files
    with open(meta_dir / "train.txt", "r") as f:
        train_files = [line.strip() for line in f.readlines()]
        
    with open(meta_dir / "test.txt", "r") as f:
        val_files = [line.strip() for line in f.readlines()]
        
    # Helper to copy files
    def copy_files(file_list, split_name):
        print(f"Processing {split_name} set...")
        for file_path in tqdm(file_list):
            class_name = file_path.split("/")[0]
            src = images_dir / f"{file_path}.jpg"
            dst_dir = YOLO_DIR / split_name / class_name
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst_dir / f"{src.name}")

    copy_files(train_files, "train")
    copy_files(val_files, "val")
    
    print(f"Dataset prepared at {YOLO_DIR}")

if __name__ == "__main__":
    try:
        download_and_extract()
        prepare_for_yolo_classification()
        print("Done! You can now train a classifier using: yolo classify train data=datasets/food-101-yolo model=yolov8n-cls.pt epochs=10")
    except Exception as e:
        print(f"Error: {e}")
