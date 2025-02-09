import mss 
import numpy as np 
import time
import cv2 
import pyautogui
import threading

class ScreenCursorMonitor:
    def __init__(self):
        self.prev_screen = self.capture_screen()
        self.prev_cursor = self.capture_cursor_area()

    def capture_screen(self):
        """Capture the full screen and return as a NumPy array."""
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[2])  # Adjust monitor index if needed
            img = np.array(screenshot)  # Convert to NumPy array
            return img

    def capture_cursor_area(self, size=50):
        """Capture a small region around the cursor and return as a NumPy array."""
        with mss.mss() as sct:
            x, y = pyautogui.position()
            region = {
                'top': max(y - size, 0),
                'left': max(x - size, 0),
                'width': size * 2,
                'height': size * 2
            }
            screenshot = sct.grab(region)  # Capture only the cursor region
            return np.array(screenshot)

    def detect_changes(self):
        """Detect changes in both full screen and cursor movement."""
        while True:
            time.sleep(0.1)  # Faster detection

            # Capture new frames
            new_screen = self.capture_screen()
            new_cursor = self.capture_cursor_area()

            # Compute differences
            screen_diff = cv2.absdiff(cv2.cvtColor(self.prev_screen, cv2.COLOR_BGR2GRAY),
                                      cv2.cvtColor(new_screen, cv2.COLOR_BGR2GRAY))

            cursor_diff = cv2.absdiff(cv2.cvtColor(self.prev_cursor, cv2.COLOR_BGR2GRAY),
                                      cv2.cvtColor(new_cursor, cv2.COLOR_BGR2GRAY))

            # Sensitivity tuning
            screen_change = screen_diff.mean() > 0.5
            cursor_change = cursor_diff.mean() > 1  

            if screen_change:
                print("Screen changed!")

            if cursor_change:
                print("Cursor moved!")

            # Update previous frames
            self.prev_screen = new_screen
            self.prev_cursor = new_cursor

    def start_monitoring(self):
        """Start the detection in a background thread."""
        detection_thread = threading.Thread(target=self.detect_changes, daemon=True)
        detection_thread.start()


if __name__ == "__main__":
    monitor = ScreenCursorMonitor()  # Create an instance of the monitor
    monitor.start_monitoring()  # Start detecting in the background
    
    test = True

    while test:
        print("Main program is running...")
        
        
        hello = input("Enter 1 to stop the program: ")
        
        if hello == "1":  # Check if input is exactly "1"
            test = False
            print("Stopping the program...")


    
