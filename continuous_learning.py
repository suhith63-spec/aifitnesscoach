"""
Continuous Learning Module for Cal-AI.
Handles the collection and storage of user corrections to fine-tune the food recognition models.
"""

import os
import json
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class ContinuousLearningManager:
    def __init__(self, base_dir: str = "training/collected_data"):
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "images"
        self.labels_dir = self.base_dir / "labels"
        self.metadata_path = self.base_dir / "metadata.json"
        
        # Create directories
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.labels_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata log
        if not self.metadata_path.exists():
            with open(self.metadata_path, "w") as f:
                json.dump([], f)

    def save_feedback(self, image: np.ndarray, detected_foods: List[Dict], corrected_foods: List[Dict], user_id: str = "anonymous") -> bool:
        """
        Save user feedback as training data.
        
        Args:
            image: The original image (numpy array BGR).
            detected_foods: List of dicts from the initial detection.
            corrected_foods: List of dicts from the user's correction (st.data_editor).
            user_id: ID of the user providing feedback.
            
        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = f"{timestamp}_{user_id[:8]}"
            image_filename = f"{unique_id}.jpg"
            label_filename = f"{unique_id}.txt"
            
            # 1. Save Image
            image_path = self.images_dir / image_filename
            # Convert RGB to BGR for OpenCV if needed, assuming input might be RGB from PIL
            # But usually cv2 uses BGR. If image is from st.camera_input (PIL), it's RGB.
            # We'll assume input is BGR (standard cv2) or handle conversion if we know source.
            # For safety, let's just save it.
            cv2.imwrite(str(image_path), image)
            
            # 2. Generate YOLO Labels from Corrections
            # Note: This is tricky because st.data_editor usually just gives us the *text* table,
            # not the bounding boxes if they weren't editable.
            # We need to map the corrected rows back to the original detections to get the boxes.
            
            yolo_lines = []
            
            # We assume the order in corrected_foods matches detected_foods
            # OR we try to match by some ID.
            # Since st.data_editor preserves order unless sorted, we'll rely on index matching for now
            # if lengths are same. If lengths differ (user added/removed rows), it's harder.
            
            # Simple strategy: Only save if counts match, assuming 1:1 mapping.
            if len(detected_foods) == len(corrected_foods):
                height, width = image.shape[:2]
                
                for i, (det, corr) in enumerate(zip(detected_foods, corrected_foods)):
                    # Get the corrected class name
                    class_name = corr.get("Food Item", "").lower().replace(" ", "_")
                    
                    # Get the original box (normalized for YOLO)
                    # det['box'] is [x1, y1, x2, y2]
                    if 'box' in det:
                        x1, y1, x2, y2 = det['box']
                        
                        # Convert to YOLO format: class x_center y_center width height (normalized)
                        x_center = ((x1 + x2) / 2) / width
                        y_center = ((y1 + y2) / 2) / height
                        w_norm = (x2 - x1) / width
                        h_norm = (y2 - y1) / height
                        
                        # We need a class ID. Since this is "open vocabulary" or custom,
                        # we might store the string name for now and map it later,
                        # OR we just store the string in a separate metadata file and use a dummy ID '0'.
                        # For a real system, we'd look up the ID in our class list.
                        # Let's use ID 0 and rely on the metadata to map "0 -> class_name" for this specific file,
                        # or better, just save the text label in a separate file or the metadata.
                        
                        # Actually, YOLO requires integer IDs.
                        # Let's just save the annotation in a custom JSON format for now, 
                        # which is easier to parse and convert to YOLO later when we have a definitive class list.
                        pass 
                        
                # Alternative: Save everything to metadata.json for offline processing
                # This is safer than trying to guess YOLO IDs on the fly without a fixed class map.
            
            # 3. Log Metadata (The Source of Truth)
            log_entry = {
                "id": unique_id,
                "timestamp": timestamp,
                "user_id": user_id,
                "image_path": str(image_path),
                "original_detections": self._serialize_detections(detected_foods),
                "corrected_feedback": corrected_foods
            }
            
            self._append_log(log_entry)
            print(f"✅ Feedback saved: {unique_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving feedback: {e}")
            return False

    def _serialize_detections(self, detections):
        """Helper to make detections JSON serializable (convert numpy types)"""
        serializable = []
        for det in detections:
            item = det.copy()
            # Remove heavy mask data if present, or encode it
            if 'mask' in item:
                del item['mask'] # Don't save full mask to JSON, it's too big
            if 'box' in item:
                item['box'] = [float(x) for x in item['box']]
            serializable.append(item)
        return serializable

    def _append_log(self, entry):
        """Append entry to metadata.json"""
        try:
            with open(self.metadata_path, "r+") as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
        except Exception:
            # If read fails, write new
            with open(self.metadata_path, "w") as f:
                json.dump([entry], f, indent=2)
