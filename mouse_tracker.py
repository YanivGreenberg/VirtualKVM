import time
import pyautogui


class MouseTracker:
    def __init__(self):
        """Handles tracking the mouse position and calculating velocity."""
        self.prev_x, self.prev_y = None, None
        self.prev_time = None

    def get_velocity(self,x,y):
        """Calculates velocity based on the current and previous mouse position."""
        current_time = time.time()

        
        if self.prev_x is None or self.prev_y is None or self.prev_time is None:
            self.prev_x, self.prev_y, self.prev_time = x, y, current_time
            return 0, 0

        time_diff = current_time - self.prev_time
        if time_diff == 0:
            return 0, 0  

        velocity_x = (x - self.prev_x) / time_diff  
        velocity_y = (y - self.prev_y) / time_diff  

        
        self.prev_x, self.prev_y, self.prev_time = x, y, current_time

        return velocity_x, velocity_y
