import mss
import numpy as np

class ScreenCapture:
    def __init__(self, region=None):
        """Handles screen capturing, allowing full-screen or specific region capture."""
        self.region = region if region else self.get_full_screen_roi()

    def get_full_screen_roi(self):
        """Automatically sets the ROI to cover all connected monitors."""
        with mss.mss() as sct:
            monitors = sct.monitors[1:] 
            
            left = min(monitor["left"] for monitor in monitors)
            top = min(monitor["top"] for monitor in monitors)
            right = max(monitor["left"] + monitor["width"] for monitor in monitors)
            bottom = max(monitor["top"] + monitor["height"] for monitor in monitors)
            
            return {
                "top": top,
                "left": left,
                "width": right - left,
                "height": bottom - top
            }

    def capture(self):
        """Capture only the defined region of the screen."""
        with mss.mss() as sct:
            screenshot = sct.grab(self.region)
            return np.array(screenshot)