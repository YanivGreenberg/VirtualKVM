import time
import threading

class ScreenCursorMonitor:
    def __init__(self, screen_capture, mouse_capture, screen_detector, cursor_detector):
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

        self.prev_screen = self.screen_capture.capture()
        self.prev_cursor = self.mouse_capture.capture_cursor_area()

        self.running = False  # Flag to control the monitoring loop
        self.thread = None  # Thread reference

    def detect_changes(self):
        """Continuously monitors for screen and cursor changes."""
        while self.running:
            time.sleep(0.1)  # Adjust for performance

            new_screen = self.screen_capture.capture()
            new_cursor = self.mouse_capture.capture_cursor_area()

            if self.screen_detector.has_changed(self.prev_screen, new_screen):
                print("Change detected in ROI!")

            if self.cursor_detector.has_changed(self.prev_cursor, new_cursor):
                print("Cursor moved inside ROI!")

            # Update previous frames
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
            self.thread.join()  # Ensure the thread finishes execution
            print("Monitoring stopped.")
