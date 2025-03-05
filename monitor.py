import time
import threading
from edge_detector import ScreenEdgeDetector
from pynput import mouse
from observer import Observer
from mouse_tracker import MouseTracker
from edge_detector import Direction


class ScreenCursorMonitor(Observer):
    def __init__(self,region,border):
        self.cursor_tracker = MouseTracker()
        self.screen_edge_detector = ScreenEdgeDetector(10,region)
        self.running = False  
        self.thread = None  
        self.block_mouse = False
        self.border = border
    
    def update(self,direction):
        if direction == Direction.LEFT and self.border == Direction.LEFT:
            print("LEFT")
            self.on_switch_monitor()
            time.sleep(3)
            self.on_switch_monitor()
        elif direction == Direction.RIGHT and self.border == Direction.RIGHT:
            print("RIGHT")
        elif direction == Direction.UP and self.border == Direction.UP:
            print("UP")
        elif direction == Direction.DOWN and self.border == Direction.DOWN:
            print("DOWN")
        else:
            pass

    def start_monitoring(self):
        """Runs detection in a background thread."""
        if not self.running:
            self.running = True
            self.listener = mouse.Listener(on_move=self.on_mouse_move, suppress=self.block_mouse)
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

    def on_switch_monitor(self):
        self.block_mouse = not self.block_mouse

