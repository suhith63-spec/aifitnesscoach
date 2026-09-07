"""
Script to train YOLOv8 model on food datasets.
This script assumes data has been prepared in 'datasets/food-101-yolo' or 'datasets/nutrition5k-yolo'.
"""

from ultralytics import YOLO
import os
from pathlib import Path

def train_food_model(dataset_yaml="datasets/food-101-yolo/data.yaml", epochs=50, img_size=640):
    """
    Fine-tune YOLOv8 on food dataset.
    
    Args:
        dataset_yaml: Path to dataset configuration file
        epochs: Number of training epochs
        img_size: Image size for training
    """
    print(f"🚀 Starting YOLOv8 training on {dataset_yaml}...")
    
    # Check if dataset config exists
    if not os.path.exists(dataset_yaml):
        print(f"❌ Dataset config not found at {dataset_yaml}")
        print("Please run the preparation scripts first!")
        return

    # Load a pretrained model
    # yolov8n-seg.pt for segmentation (if using Nutrition5k)
    # yolov8n-cls.pt for classification (if using Food-101)
    
    # Auto-detect task based on yaml path (heuristic)
    if "cls" in dataset_yaml or "food-101" in dataset_yaml:
        model_name = "yolov8n-cls.pt"
        task = "classify"
    else:
        model_name = "yolov8n-seg.pt"
        task = "segment"
        
    print(f"Loading {model_name} for {task} task...")
    model = YOLO(model_name)
    
    # Train the model
    results = model.train(
        data=dataset_yaml,
        epochs=epochs,
        imgsz=img_size,
        patience=10,
        batch=16,
        name="food_model_v1",
        device=0 if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu" # Auto-select GPU
    )
    
    print("✅ Training complete!")
    print(f"Best model saved to: {results.save_dir}/weights/best.pt")
    
    # Copy best model to main models directory
    os.makedirs("models", exist_ok=True)
    import shutil
    shutil.copy(f"{results.save_dir}/weights/best.pt", "models/best_food_model.pt")
    print("Saved to models/best_food_model.pt")

if __name__ == "__main__":
    # Example usage
    # train_food_model("datasets/food-101-yolo/data.yaml")
    print("Edit this script to point to your generated data.yaml file.")
    print("Usage: python training/train_yolo.py")
