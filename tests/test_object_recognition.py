import pytest
from src.python.ai.object_recognition import ObjectRecognitionModule, IndigenousTermMapper
from PIL import Image
import numpy as np

@pytest.fixture
def test_image():
    # Create a test image
    img = Image.new('RGB', (224, 224), color='red')
    img.save('test_image.jpg')
    return 'test_image.jpg'

def test_object_recognition_module(test_image):
    module = ObjectRecognitionModule()
    detections = module.process_image(test_image)
    
    assert isinstance(detections, list)
    for detection in detections:
        assert 'label' in detection
        assert 'confidence' in detection
        assert 'bbox' in detection
        assert isinstance(detection['confidence'], float)
        assert 0 <= detection['confidence'] <= 1

def test_indigenous_term_mapper():
    mapper = IndigenousTermMapper('xhosa')
    
    # Test getting existing term
    term = mapper.get_indigenous_term('tree')
    assert isinstance(term, str)
    assert len(term) > 0
    
    # Test getting non-existent term
    term = mapper.get_indigenous_term('nonexistent')
    assert 'not found' in term.lower()
    
    # Test adding new term
    mapper.add_new_term('book', 'incwadi')
    term = mapper.get_indigenous_term('book')
    assert term == 'incwadi'