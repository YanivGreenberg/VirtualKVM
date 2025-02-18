import cv2
from abc import ABC, abstractmethod

class ChangeDetectionStrategy(ABC):
    @abstractmethod
    def has_changed(self, old_frame, new_frame) -> bool:
        pass

class BasicChangeDetection(ChangeDetectionStrategy):
    def __init__(self, threshold=0.3):
        self.threshold = threshold

    def has_changed(self, old_frame, new_frame) -> bool:
        """Detects change based on grayscale difference."""
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        new_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(old_gray, new_gray)
        return diff.mean() > self.threshold

class ScreenEdgeDetector:
    def __init__(self, threshold = 10, region = None):
        self.threshold = threshold
        self.width = region["width"]
        self.height = region["height"]
    
    def on_move(self, x, y, velocity_x, velocity_y):
        left, right, down, up = False, False, False, False
        if x <= self.threshold and velocity_x < 0:
            left = True
        elif x >= self.width - self.threshold and velocity_x > 0:
            right = True
        if y <= self.threshold and velocity_y < 0:
            up = True
        elif y >= self.height - self.threshold and velocity_y > 0:
            down = True
        return left,right,up,down
        
