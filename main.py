from edge_detector import ScreenEdgeDetector
from monitor import ScreenCursorMonitor
import mss

def get_full_screen_roi():
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

if __name__ == "__main__":
    monitor = ScreenCursorMonitor(get_full_screen_roi())
    ScreenEdgeDetector.attach(monitor)
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
