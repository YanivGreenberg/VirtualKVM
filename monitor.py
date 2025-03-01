import time
import threading
from edge_detector import ScreenEdgeDetector
from pynput import mouse
from observer import Observer
from mouse_tracker import MouseTracker


class ScreenCursorMonitor(Observer):
    def __init__(self,region):
        self.cursor_tracker = MouseTracker()
        self.screen_edge_detector = ScreenEdgeDetector(10,region)
        self.running = False  
        self.thread = None  
    
    def update(self,direction):
        if direction == 1:
            pass
        elif direction == 2:
            pass
        elif direction == 3:
            pass
        else:
            pass

    def start_monitoring(self):
        """Runs detection in a background thread."""
        if not self.running:
            self.running = True
            self.listener = mouse.Listener(on_move=self.on_mouse_move)
            self.listener.start()
            print("Monitoring started...")

    def stop_monitoring(self):
        """Stops the monitoring loop."""
        self.running = False
        if self.listener:
            self.listener.stop()  
            print("Monitoring stopped.")

    def on_mouse_move(self,x, y):
        print(x,y)
        velocity_x, velocity_y = self.cursor_tracker.get_velocity(x,y)
        self.screen_edge_detector.detect_moving_to_edge(x,y,velocity_x,velocity_y)
