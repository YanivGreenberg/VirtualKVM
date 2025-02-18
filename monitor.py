import time
import threading
from change_detection import ScreenEdgeDetector

class ScreenCursorMonitor:
    def __init__(self, screen_capture, mouse_capture, screen_detector, cursor_detector,cursor_tracker):
        """
        Monitors screen and cursor for changes.
        :param screen_capture: Handles screen capturing
        :param mouse_capture: Handles cursor capturing
        :param screen_detector: Detects changes in screen content
        :param cursor_detector: Detects cursor movement changes
        """
        self.screen_capture = screen_capture
        self.mouse_capture = mouse_capture
        self.screen_detector = screen_detector
        self.cursor_detector = cursor_detector
        self.cursor_tracker = cursor_tracker

        self.prev_screen = self.screen_capture.capture()
        self.prev_cursor = self.mouse_capture.capture_cursor_area()

        self.left_side = False
        self.right_side = False
        self.up_side = False
        self.down_side = False

        self.running = False  
        self.thread = None  

    def detect_changes(self):
        """Continuously monitors for screen and cursor changes."""
        screen_edge_detector = ScreenEdgeDetector(10,self.screen_capture.region)
        while self.running:
            time.sleep(0.1)  

            new_screen = self.screen_capture.capture()
            new_cursor = self.mouse_capture.capture_cursor_area()

            if self.screen_detector.has_changed(self.prev_screen, new_screen):
                print("Change detected in ROI!")

            if self.cursor_detector.has_changed(self.prev_cursor, new_cursor):
                print("Cursor moved inside ROI!")
                velocity_x, velocity_y = self.cursor_tracker.get_velocity()
                self.left_side,self.right_side,self.up_side,self.down_side = screen_edge_detector.detect_moving_to_edge(self.cursor_tracker.prev_x,self.cursor_tracker.prev_y,velocity_x,velocity_y)
                print(f"left {self.left_side}, right {self.right_side}, up {self.up_side}, down {self.down_side}")


            self.prev_screen = new_screen
            self.prev_cursor = new_cursor

    def start_monitoring(self):
        """Runs detection in a background thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.detect_changes, daemon=True)
            self.thread.start()
            print("Monitoring started...")

    def stop_monitoring(self):
        """Stops the monitoring loop."""
        self.running = False
        if self.thread:
            self.thread.join()  
            print("Monitoring stopped.")
