import numpy as np
import torch
from segment_anything import SamPredictor, sam_model_registry
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SegmentedObject:
    mask: np.ndarray
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center_point: Tuple[int, int]
    area: int

class SAMObjectDetector:
    def __init__(self, model_type: str = "vit_h"):
        """Initialize SAM model for object detection
        
        Args:
            model_type: One of 'vit_h', 'vit_l', 'vit_b' for different model sizes
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # Load SAM model
        self.sam = sam_model_registry[model_type](checkpoint="sam_vit_h_4b8939.pth")
        self.sam.to(device=self.device)
        self.predictor = SamPredictor(self.sam)

    def set_image(self, image: np.ndarray) -> None:
        """Set the image for SAM to process"""
        self.predictor.set_image(image)

    def detect_object_at_point(self, point: Tuple[int, int]) -> Optional[SegmentedObject]:
        """Detect and segment object at given point
        
        Args:
            point: (x, y) coordinates where to detect object
            
        Returns:
            SegmentedObject if found, None otherwise
        """
        # Convert point to format expected by SAM
        input_point = np.array([[point[0], point[1]]])
        input_label = np.array([1])  # 1 indicates foreground

        # Generate mask
        masks, scores, _ = self.predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True
        )

        if len(masks) == 0:
            return None

        # Get best mask
        best_mask_idx = np.argmax(scores)
        mask = masks[best_mask_idx]
        score = scores[best_mask_idx]

        # Calculate bounding box
        y_indices, x_indices = np.where(mask)
        if len(y_indices) == 0 or len(x_indices) == 0:
            return None

        x1, x2 = np.min(x_indices), np.max(x_indices)
        y1, y2 = np.min(y_indices), np.max(y_indices)

        # Calculate center point
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        return SegmentedObject(
            mask=mask,
            confidence=float(score),
            bbox=(int(x1), int(y1), int(x2), int(y2)),
            center_point=(int(center_x), int(center_y)),
            area=int(np.sum(mask))
        )

    def detect_all_objects(self) -> List[SegmentedObject]:
        """Detect and segment all objects in the image"""
        # Generate automatic mask proposals
        masks = self.predictor.generate()
        
        objects = []
        for i, (mask, score) in enumerate(zip(masks, scores)):
            if score < 0.5:  # Filter low confidence detections
                continue

            y_indices, x_indices = np.where(mask)
            if len(y_indices) == 0 or len(x_indices) == 0:
                continue

            x1, x2 = np.min(x_indices), np.max(x_indices)
            y1, y2 = np.min(y_indices), np.max(y_indices)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            objects.append(SegmentedObject(
                mask=mask,
                confidence=float(score),
                bbox=(int(x1), int(y1), int(x2), int(y2)),
                center_point=(int(center_x), int(center_y)),
                area=int(np.sum(mask))
            ))

        return objects

    def get_object_attributes(self, segmented_obj: SegmentedObject) -> Dict[str, any]:
        """Get additional attributes about the segmented object"""
        mask = segmented_obj.mask
        
        # Calculate shape attributes
        perimeter = self._calculate_perimeter(mask)
        circularity = 4 * np.pi * segmented_obj.area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Calculate position attributes
        bbox_width = segmented_obj.bbox[2] - segmented_obj.bbox[0]
        bbox_height = segmented_obj.bbox[3] - segmented_obj.bbox[1]
        aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 0
        
        return {
            'area': segmented_obj.area,
            'perimeter': perimeter,
            'circularity': circularity,
            'aspect_ratio': aspect_ratio,
            'bbox_dimensions': (bbox_width, bbox_height),
            'relative_position': segmented_obj.center_point
        }

    def _calculate_perimeter(self, mask: np.ndarray) -> float:
        """Calculate the perimeter of a binary mask"""
        from scipy import ndimage
        
        # Use morphological gradient to find boundary
        struct = ndimage.generate_binary_structure(2, 2)
        dilated = ndimage.binary_dilation(mask, struct)
        eroded = ndimage.binary_erosion(mask, struct)
        boundary = dilated & ~eroded
        
        return float(np.sum(boundary))