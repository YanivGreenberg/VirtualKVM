import mss
import numpy as np
import pyautogui

class MouseCapture:
    def __init__(self, screen_region):
        """Handles capturing a small area around the mouse cursor."""
        self.region = screen_region  

    def capture_cursor_area(self, size=50):
        """Capture a small region around the cursor, only if inside the monitoring bounds."""
        x, y = pyautogui.position()
        if not (self.region["left"] <= x <= self.region["left"] + self.region["width"] and
                self.region["top"] <= y <= self.region["top"] + self.region["height"]):
            return np.zeros((size * 2, size * 2, 3), dtype=np.uint8)  
        with mss.mss() as sct:
            region = {
                'top': max(y - size, 0),
                'left': max(x - size, 0),
                'width': size * 2,
                'height': size * 2
            }
            screenshot = sct.grab(region)
            return np.array(screenshot)