from screen_capture import ScreenCapture
from mouse_capture import MouseCapture
from change_detection import BasicChangeDetection
from monitor import ScreenCursorMonitor
from mouse_tracker import MouseTracker

if __name__ == "__main__":
    screen_capture = ScreenCapture()  # Capturing service
    mouse_capture = MouseCapture(screen_capture.region)  # Cursor capture service
    screen_detector = BasicChangeDetection(threshold=0.3)  # Screen change detection
    cursor_detector = BasicChangeDetection(threshold=1)  # Cursor change detection
    cursor_tracker = MouseTracker()

    monitor = ScreenCursorMonitor(screen_capture, mouse_capture, screen_detector, cursor_detector,cursor_tracker)
    monitor.start_monitoring()

    try:
        while True:
            command = input("Enter 1 to stop the program: ")
            if command == "1":
                monitor.stop_monitoring()
                print("Stopping the program...")
                break
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\nProgram interrupted. Exiting gracefully...")
