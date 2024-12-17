from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from .sam_integration import SAMObjectDetector, SegmentedObject
from .object_learning import ObjectTerm
from .knowledge_base import KnowledgeBase

@dataclass
class EnhancedObjectTerm(ObjectTerm):
    visual_attributes: Dict[str, any] = None
    segmentation_mask: Optional[np.ndarray] = None
    related_terms: List[str] = None

class EnhancedObjectLearner:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.sam = SAMObjectDetector()
        self.min_confidence = 0.7

    async def learn_from_image(self,
                           image: np.ndarray,
                           point: Tuple[int, int],
                           term: EnhancedObjectTerm) -> Dict[str, any]:
        """Learn a new object term with visual understanding
        
        Args:
            image: Image array (H, W, C)
            point: (x, y) coordinates where user clicked
            term: Enhanced object term to learn
            
        Returns:
            Dict containing learning results
        """
        # Set image in SAM
        self.sam.set_image(image)

        # Detect object at point
        segmented_obj = self.sam.detect_object_at_point(point)
        if not segmented_obj or segmented_obj.confidence < self.min_confidence:
            return {
                'success': False,
                'error': 'Could not detect object clearly'
            }

        # Get object attributes
        visual_attrs = self.sam.get_object_attributes(segmented_obj)

        # Update term with visual information
        term.visual_attributes = visual_attrs
        term.segmentation_mask = segmented_obj.mask

        # Store in knowledge base
        await self.kb.add_translation(term)

        # Find visually similar objects
        similar_terms = await self._find_similar_objects(visual_attrs)
        term.related_terms = [t.local_term for t in similar_terms]

        return {
            'success': True,
            'term': term,
            'confidence': segmented_obj.confidence,
            'similar_terms': similar_terms
        }

    async def identify_objects(self,
                           image: np.ndarray,
                           language: str) -> List[Dict[str, any]]:
        """Identify all objects in image and get their local terms"""
        # Set image in SAM
        self.sam.set_image(image)

        # Detect all objects
        objects = self.sam.detect_all_objects()

        results = []
        for obj in objects:
            if obj.confidence < self.min_confidence:
                continue

            # Get object attributes
            visual_attrs = self.sam.get_object_attributes(obj)

            # Find matching terms
            similar_terms = await self._find_similar_objects(visual_attrs)
            terms_in_language = [t for t in similar_terms if t.language == language]

            results.append({
                'bbox': obj.bbox,
                'confidence': obj.confidence,
                'center': obj.center_point,
                'terms': terms_in_language,
                'attributes': visual_attrs
            })

        return results

    async def _find_similar_objects(self,
                                visual_attrs: Dict[str, any],
                                threshold: float = 0.8
                                ) -> List[EnhancedObjectTerm]:
        """Find objects with similar visual attributes"""
        # Get all terms from knowledge base
        all_terms = await self.kb.get_all_terms()
        similar_terms = []

        for term in all_terms:
            if not term.visual_attributes:
                continue

            # Calculate similarity score
            similarity = self._calculate_visual_similarity(
                visual_attrs,
                term.visual_attributes
            )

            if similarity >= threshold:
                similar_terms.append(term)

        return similar_terms

    def _calculate_visual_similarity(self,
                                 attrs1: Dict[str, any],
                                 attrs2: Dict[str, any]) -> float:
        """Calculate similarity between visual attributes"""
        # Compare shape attributes
        area_diff = abs(attrs1['area'] - attrs2['area']) / max(attrs1['area'], attrs2['area'])
        circ_diff = abs(attrs1['circularity'] - attrs2['circularity'])
        ratio_diff = abs(attrs1['aspect_ratio'] - attrs2['aspect_ratio'])

        # Weighted similarity score
        weights = {
            'area': 0.3,
            'circularity': 0.4,
            'aspect_ratio': 0.3
        }

        similarity = (
            (1 - area_diff) * weights['area'] +
            (1 - circ_diff) * weights['circularity'] +
            (1 - ratio_diff) * weights['aspect_ratio']
        )

        return similarity