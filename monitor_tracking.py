import mss 
import numpy as np 
import time
import cv2 
import pyautogui
import threading

class ScreenCursorMonitor:
    def __init__(self, region=None):
        """
        Initialize the monitor with a defined bounding box (region).
        :param region: A dictionary defining 'top', 'left', 'width', and 'height'.
        """
        self.region = region if region else self.select_roi()  # Ask user for ROI if none is provided
        print(f"Monitoring region: {self.region}")
        
        self.prev_screen = self.capture_screen()
        self.prev_cursor = self.capture_cursor_area()

    def select_roi(self):
        """Allows the user to manually select an ROI using mouse position."""
        input("Move your mouse to the **top-left** corner of the ROI and press Enter...")
        x1, y1 = pyautogui.position()

        input("Move your mouse to the **bottom-right** corner of the ROI and press Enter...")
        x2, y2 = pyautogui.position()

        return {
            "top": min(y1, y2),
            "left": min(x1, x2),
            "width": abs(x2 - x1),
            "height": abs(y2 - y1)
        }

    def capture_screen(self):
        """Capture only the defined region of the screen."""
        with mss.mss() as sct:
            screenshot = sct.grab(self.region)
            return np.array(screenshot)  

    def capture_cursor_area(self, size=50):
        """Capture a small region around the cursor, only if inside the monitoring bounds."""
        x, y = pyautogui.position()

        if not (self.region["left"] <= x <= self.region["left"] + self.region["width"] and
                self.region["top"] <= y <= self.region["top"] + self.region["height"]):
            return np.zeros((size * 2, size * 2, 3), dtype=np.uint8)  # Return blank if cursor is outside ROI

        with mss.mss() as sct:
            region = {
                'top': max(y - size, 0),
                'left': max(x - size, 0),
                'width': size * 2,
                'height': size * 2
            }
            screenshot = sct.grab(region)
            return np.array(screenshot)

    def detect_changes(self):
        """Detect changes within the specified region only."""
        while True:
            time.sleep(0.1)  # Faster detection

            new_screen = self.capture_screen()
            new_cursor = self.capture_cursor_area()

            # Compute differences only in the selected region
            screen_diff = cv2.absdiff(cv2.cvtColor(self.prev_screen, cv2.COLOR_BGR2GRAY),
                                      cv2.cvtColor(new_screen, cv2.COLOR_BGR2GRAY))

            cursor_diff = cv2.absdiff(cv2.cvtColor(self.prev_cursor, cv2.COLOR_BGR2GRAY),
                                      cv2.cvtColor(new_cursor, cv2.COLOR_BGR2GRAY))

            # Sensitivity tuning
            screen_change = screen_diff.mean() > 0.3
            cursor_change = cursor_diff.mean() > 1  

            if screen_change:
                print("Change detected in ROI!")

            if cursor_change:
                print("Cursor moved inside ROI!")

            # Update previous frames
            self.prev_screen = new_screen
            self.prev_cursor = new_cursor

    def start_monitoring(self):
        """Start the detection in a background thread."""
        detection_thread = threading.Thread(target=self.detect_changes, daemon=True)
        detection_thread.start()


if __name__ == "__main__":
    monitor = ScreenCursorMonitor()  # Select ROI dynamically and start monitoring
    monitor.start_monitoring()  

    test = True

    while test:
        print("Main program is running...")
        hello = input("Enter 1 to stop the program: ")
        if hello == "1":
            test = False
            print("Stopping the program...")
