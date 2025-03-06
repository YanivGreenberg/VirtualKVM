import time
import threading
from edge_detector import ScreenEdgeDetector
from pynput import mouse
from observer import Observer
from mouse_tracker import MouseTracker
from pynput.mouse import Controller
import ctypes
import win32api
import win32con

class ScreenCursorMonitor(Observer):
    def __init__(self,region,border):
        self.cursor_tracker = MouseTracker()
        self.screen_edge_detector = ScreenEdgeDetector(10,region)
        self.running = False   
        self.block_mouse = False
        self.border = border
        self.mouse_controller = None
        dll_name = r'mouse_control.dll'
        dll_handle = win32api.LoadLibraryEx(dll_name, 0, win32con.LOAD_WITH_ALTERED_SEARCH_PATH)
        self.mouse_lib = ctypes.WinDLL(dll_name, handle=dll_handle)
        self.mouse_lib.EnableMouse.argtypes = [ctypes.c_bool]
        self.mouse_lib.EnableMouse.restype = None
        CALLBACK_TYPE = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_int)
        self.mouse_callback = CALLBACK_TYPE(self.on_mouse_move)
        self.mouse_lib.SetMouseCallback(self.mouse_callback)
        timer = threading.Timer(30,lambda: self.mouse_lib.EnableMouse(True))
        timer.start()


    def update(self,direction):
        if self.border == direction:
            self.mouse_lib.EnableMouse(False)

            


    def start_monitoring(self):
        """Runs detection in a background thread."""
        if not self.running:
            self.mouse_controller = Controller() 
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

    def on_switch_monitor(self):
        self.block_mouse = not self.block_mouse
        print(self.block_mouse)

