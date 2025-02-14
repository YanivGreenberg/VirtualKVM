import mss
import numpy as np

class ScreenCapture:
    def __init__(self, region=None):
        """Handles screen capturing, allowing full-screen or specific region capture."""
        self.region = region if region else self.get_full_screen_roi()

    def get_full_screen_roi(self):
        """Automatically sets the ROI to cover the full primary monitor."""
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor (index 1)
            return {
                "top": monitor["top"],
                "left": monitor["left"],
                "width": monitor["width"],
                "height": monitor["height"]
            }

    def capture(self):
        """Capture only the defined region of the screen."""
        with mss.mss() as sct:
            screenshot = sct.grab(self.region)
            return np.array(screenshot)