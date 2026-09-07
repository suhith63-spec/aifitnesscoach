"""
Cal-AI: Computer Vision Nutrition System
Implements legendary-level calorie estimation using YOLOv8 segmentation and volume estimation.
"""

import os
import cv2
import numpy as np
import json
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import streamlit as st

# Try to import ultralytics for YOLOv8
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️ Ultralytics not found. Cal-AI will run in mock mode.")

class NutritionKnowledgeBase:
    """
    Database mapping food classes to nutritional density.
    Uses USDA data approximations.
    """
    def __init__(self):
        # Map YOLO classes (COCO) and custom food classes to nutrition info
        # Format: {class_name: {calories_per_100g, density_g_cm3, macros}}
        self.food_db = {
            # Standard COCO classes that are food
            "apple": {"calories": 52, "density": 0.8, "protein": 0.3, "carbs": 14, "fat": 0.2},
            "banana": {"calories": 89, "density": 0.9, "protein": 1.1, "carbs": 23, "fat": 0.3},
            "sandwich": {"calories": 250, "density": 0.5, "protein": 13, "carbs": 30, "fat": 10},
            "orange": {"calories": 47, "density": 0.85, "protein": 0.9, "carbs": 12, "fat": 0.1},
            "broccoli": {"calories": 34, "density": 0.37, "protein": 2.8, "carbs": 7, "fat": 0.4},
            "carrot": {"calories": 41, "density": 0.64, "protein": 0.9, "carbs": 10, "fat": 0.2},
            "hot dog": {"calories": 290, "density": 0.7, "protein": 10, "carbs": 25, "fat": 15},
            "pizza": {"calories": 266, "density": 0.6, "protein": 11, "carbs": 33, "fat": 10},
            "donut": {"calories": 452, "density": 0.4, "protein": 4.9, "carbs": 51, "fat": 25},
            "cake": {"calories": 371, "density": 0.45, "protein": 5.5, "carbs": 53, "fat": 15},
            "bowl": {"calories": 200, "density": 0.7, "protein": 5, "carbs": 30, "fat": 5}, # Common misdetection container
            "cup": {"calories": 100, "density": 1.0, "protein": 0, "carbs": 20, "fat": 0},
            
            # Expanded common foods
            "rice": {"calories": 130, "density": 0.75, "protein": 2.7, "carbs": 28, "fat": 0.3},
            "chicken": {"calories": 165, "density": 1.05, "protein": 31, "carbs": 0, "fat": 3.6},
            "salad": {"calories": 30, "density": 0.3, "protein": 1, "carbs": 3, "fat": 2},
            "burger": {"calories": 295, "density": 0.6, "protein": 17, "carbs": 30, "fat": 14},
            "pasta": {"calories": 131, "density": 0.65, "protein": 5, "carbs": 25, "fat": 1},
            "steak": {"calories": 271, "density": 1.1, "protein": 26, "carbs": 0, "fat": 19},
            "fish": {"calories": 206, "density": 1.0, "protein": 22, "carbs": 0, "fat": 12},
            "egg": {"calories": 155, "density": 1.0, "protein": 13, "carbs": 1.1, "fat": 11},
            "bread": {"calories": 265, "density": 0.3, "protein": 9, "carbs": 49, "fat": 3},
            "potato": {"calories": 77, "density": 0.7, "protein": 2, "carbs": 17, "fat": 0.1},
            
            # Generic fallbacks
            "fruit": {"calories": 60, "density": 0.8, "protein": 1, "carbs": 15, "fat": 0.5},
            "vegetable": {"calories": 30, "density": 0.5, "protein": 2, "carbs": 6, "fat": 0.2},
            "meat": {"calories": 250, "density": 1.1, "protein": 26, "carbs": 0, "fat": 15},
            "grain": {"calories": 130, "density": 0.7, "protein": 4, "carbs": 28, "fat": 1},
        }
    
    def get_nutrition(self, class_name: str) -> Dict[str, float]:
        """Get nutrition data for a class, with fallback"""
        class_name = class_name.lower()
        if class_name in self.food_db:
            return self.food_db[class_name]
        
        # Fuzzy matching or fallback
        for key in self.food_db:
            if key in class_name:
                return self.food_db[key]
        
        # Default fallback
        print(f"⚠️ Nutrition info not found for '{class_name}', using generic fallback.")
        return {"calories": 150, "density": 0.8, "protein": 5, "carbs": 20, "fat": 5}

class VolumeEstimator:
    """
    Estimates food volume using reference objects and shape priors.
    """
    def __init__(self):
        # Reference object dimensions (diameter/width in cm)
        self.references = {
            "coin": 2.5,  # ~1 inch / quarter
            "credit_card": 8.5, # width
            "thumb": 2.5, # approximation
        }
        
    def estimate_volume(self, mask: np.ndarray, ref_pixels: float = None, ref_type: str = "coin") -> Tuple[float, float]:
        """
        Estimate volume from segmentation mask.
        
        Args:
            mask: Binary mask of the food item
            ref_pixels: Width of reference object in pixels (if known)
            ref_type: Type of reference object
            
        Returns:
            volume_cm3: Estimated volume
            confidence: Confidence score of estimation
        """
        area_pixels = np.sum(mask)
        
        if area_pixels == 0:
            return 0.0, 0.0
            
        # If no reference, assume standard plate width (25cm) covers ~80% of image width
        # This is a heuristic fallback
        if not ref_pixels:
            img_width = mask.shape[1]
            pixels_per_cm = img_width / 30.0 # Assume 30cm field of view width
        else:
            ref_cm = self.references.get(ref_type, 2.5)
            pixels_per_cm = ref_pixels / ref_cm
            
        # Area in cm2
        area_cm2 = area_pixels / (pixels_per_cm ** 2)
        
        # Height heuristic:
        # We don't have depth, so we estimate height based on area and food type priors
        # For now, we assume a "mound" shape where height is related to sqrt(area)
        # H ~ 0.5 * sqrt(area) for piled food, H ~ 1.0 for flat food
        estimated_height_cm = 0.6 * np.sqrt(area_cm2)
        
        # Volume = Area * Height
        volume_cm3 = area_cm2 * estimated_height_cm
        
        # Confidence is lower if we guessed the scale
        confidence = 0.9 if ref_pixels else 0.6
        
        return volume_cm3, confidence

class FoodDetector:
    """
    Wraps YOLOv8-seg for food detection and segmentation.
    """
    def __init__(self, model_path="yolov8n-seg.pt"):
        self.model = None
        if YOLO_AVAILABLE:
            try:
                # Check for custom trained model first
                custom_model_path = "models/best_food_model.pt"
                if os.path.exists(custom_model_path):
                    self.model = YOLO(custom_model_path)
                    print(f"✅ Loaded CUSTOM food model: {custom_model_path}")
                else:
                    # Auto-download on first run
                    self.model = YOLO(model_path)
                    print(f"✅ YOLOv8 model loaded: {model_path}")
            except Exception as e:
                print(f"⚠️ Failed to load YOLO model: {e}")
    
    def detect(self, image_path_or_array) -> List[Dict]:
        """
        Detect food items in image.
        
        Returns list of dicts:
        {
            "class": str,
            "conf": float,
            "box": [x1, y1, x2, y2],
            "mask": np.ndarray (binary)
        }
        """
        if not self.model:
            return self._mock_detect(image_path_or_array)
            
        results = self.model(image_path_or_array, verbose=False)
        detections = []
        
        for r in results:
            if r.masks is None:
                continue
                
            masks = r.masks.data.cpu().numpy()
            boxes = r.boxes.data.cpu().numpy()
            
            for i, (mask, box) in enumerate(zip(masks, boxes)):
                # box format: x1, y1, x2, y2, conf, cls
                x1, y1, x2, y2, conf, cls_id = box
                class_name = self.model.names[int(cls_id)]
                
                # Resize mask to original image size if needed
                # YOLO masks are often smaller
                if r.orig_shape != mask.shape:
                    mask = cv2.resize(mask, (r.orig_shape[1], r.orig_shape[0]))
                
                detections.append({
                    "class": class_name,
                    "conf": float(conf),
                    "box": [float(x1), float(y1), float(x2), float(y2)],
                    "mask": (mask > 0.5).astype(np.uint8)
                })
                
        return detections

    def _mock_detect(self, image) -> List[Dict]:
        """Mock detection for when YOLO is missing"""
        # Return a dummy detection in center of image
        if isinstance(image, np.ndarray):
            h, w = image.shape[:2]
        else:
            h, w = 480, 640
            
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (w//2, h//2), h//4, 1, -1)
        
        return [{
            "class": "sandwich",
            "conf": 0.95,
            "box": [w//4, h//4, w*3//4, h*3//4],
            "mask": mask
        }]

class FoodClassifier:
    """
    Stage 2: Classifies cropped food images into specific dishes (e.g., Food-101 classes).
    """
    def __init__(self, model_path="yolov8n-cls.pt"):
        self.model = None
        if YOLO_AVAILABLE:
            try:
                # Check for custom trained classifier first
                custom_model_path = "models/best_food_classifier.pt"
                if os.path.exists(custom_model_path):
                    self.model = YOLO(custom_model_path)
                    print(f"✅ Loaded CUSTOM food classifier: {custom_model_path}")
                else:
                    # Fallback to default classifier (or generic)
                    # Note: yolov8n-cls.pt is trained on ImageNet, not Food-101 by default.
                    # But the user will train their own.
                    self.model = YOLO(model_path) 
                    print(f"✅ Loaded generic classifier: {model_path}")
            except Exception as e:
                print(f"⚠️ Failed to load Classifier model: {e}")

    def classify(self, image_crop) -> Tuple[str, float]:
        """
        Classify a food crop.
        Returns (class_name, confidence)
        """
        if not self.model or image_crop.size == 0:
            return "unknown", 0.0
            
        try:
            results = self.model(image_crop, verbose=False)
            if results and results[0].probs:
                probs = results[0].probs
                top1_index = probs.top1
                top1_conf = float(probs.top1conf)
                class_name = results[0].names[top1_index]
                return class_name, top1_conf
        except Exception as e:
            print(f"Classification error: {e}")
            
        return "unknown", 0.0

class CalorieAI:
    """
    Orchestrator for the Cal-AI system.
    """
    def __init__(self):
        self.detector = FoodDetector()
        self.classifier = FoodClassifier()
        self.volume_estimator = VolumeEstimator()
        self.nutrition_kb = NutritionKnowledgeBase()
        
    def analyze_image(self, image, ref_pixels=None) -> Dict:
        """
        Full pipeline: Detect -> Segment -> Estimate Volume -> Calculate Calories
        """
        # 1. Detect
        detections = self.detector.detect(image)
        
        analyzed_items = []
        total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        
        for det in detections:
            class_name = det["class"]
            mask = det["mask"]
            box = det["box"]
            
            # 1.5 Refine Classification (Stage 2)
            # Crop the object
            x1, y1, x2, y2 = map(int, box)
            # Ensure crop is within bounds
            h, w = image.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            if x2 > x1 and y2 > y1:
                crop = image[y1:y2, x1:x2]
                refined_class, refined_conf = self.classifier.classify(crop)
                
                # If classifier is confident and gives a specific food name, use it
                # Logic: Detector might say "bowl" or "food", Classifier says "ramen"
                if refined_conf > 0.4 and refined_class != "unknown":
                    print(f"🔍 Refined: {class_name} -> {refined_class} ({refined_conf:.2f})")
                    class_name = refined_class
            
            # 2. Estimate Volume
            volume_cm3, vol_conf = self.volume_estimator.estimate_volume(mask, ref_pixels)
            
            # 3. Get Nutrition Info
            nut_info = self.nutrition_kb.get_nutrition(class_name)
            density = nut_info["density"]
            
            # 4. Calculate Mass and Macros
            mass_g = volume_cm3 * density
            
            calories = (mass_g / 100.0) * nut_info["calories"]
            protein = (mass_g / 100.0) * nut_info["protein"]
            carbs = (mass_g / 100.0) * nut_info["carbs"]
            fat = (mass_g / 100.0) * nut_info["fat"]
            
            item_result = {
                "name": class_name,
                "confidence": det["conf"],
                "volume_cm3": round(volume_cm3, 1),
                "mass_g": round(mass_g, 1),
                "calories": round(calories),
                "protein": round(protein, 1),
                "carbs": round(carbs, 1),
                "fat": round(fat, 1),
                "mask": det["mask"], # Keep for visualization
                "box": det["box"]
            }
            
            analyzed_items.append(item_result)
            
            # Aggregate totals
            total_nutrition["calories"] += calories
            total_nutrition["protein"] += protein
            total_nutrition["carbs"] += carbs
            total_nutrition["fat"] += fat
            
        return {
            "items": analyzed_items,
            "total": {k: round(v) for k, v in total_nutrition.items()},
            "image_dims": image.shape[:2]
        }

    def visualize_results(self, image, analysis_result):
        """
        Draw segmentation masks and labels on image.
        """
        vis_img = image.copy()
        
        # Create overlay for masks
        overlay = vis_img.copy()
        
        for item in analysis_result["items"]:
            mask = item["mask"]
            color = np.random.randint(0, 255, (3,), dtype=np.uint8).tolist()
            
            # Color the mask region
            vis_img[mask == 1] = vis_img[mask == 1] * 0.5 + np.array(color) * 0.5
            
            # Draw bounding box
            x1, y1, x2, y2 = map(int, item["box"])
            cv2.rectangle(vis_img, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{item['name']} {item['calories']}kcal"
            cv2.putText(vis_img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
        return vis_img

# Singleton instance
cal_ai = CalorieAI()
