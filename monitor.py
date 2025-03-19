import time
import threading
from edge_detector import ScreenEdgeDetector
from observer import Observer
from mouse_tracker import MouseTracker
import ctypes
import win32api
import win32con
from pynput import mouse
import asyncio
import os.path

class ScreenCursorMonitor(Observer):
    def __init__(self, region, border, data_queue, is_server):
        self.is_server = is_server

        self.cursor_tracker = MouseTracker()
        self.screen_edge_detector = ScreenEdgeDetector(10, region)
        self.running = False
        self.border = border
        self.mouse_controller = None
        self.listener = None
        self.data_queue = data_queue
        self.loop = asyncio.get_running_loop() 

        if self.is_server:
            self.block_mouse = False
            self.locked_x = 0
            self.locked_y = 0
            # Load the DLL
            dll_name = r'mouse_control.dll'
            if os.path.exists(dll_name):
                print(f"'{dll_name}' exists.")
            else:
                print(f"'{dll_name}' does not exist.")           
            dll_handle = win32api.LoadLibraryEx(dll_name, 0, win32con.LOAD_WITH_ALTERED_SEARCH_PATH)
            self.mouse_lib = ctypes.WinDLL(dll_name, handle=dll_handle)

            # Set the EnableMouse function argument types
            self.mouse_lib.EnableMouse.argtypes = [ctypes.c_bool]
            self.mouse_lib.EnableMouse.restype = None

            # Set the callback function type
            CALLBACK_TYPE = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_int)
            self.mouse_callback_func = self.on_mouse_move #assign function to class variable.
            self.mouse_callback = CALLBACK_TYPE(self.mouse_callback_func) #assign ctypes object to class variable.

            # Set the callback in the DLL
            self.mouse_lib.SetMouseCallback(self.mouse_callback)


    def update(self, direction):
        if self.border == direction:
            if self.is_server:
                if not self.block_mouse:
                    self.on_switch_monitor()
                    self.loop.call_soon_threadsafe(self.data_queue.put_nowait, ("mouse_set", self.locked_x, self.locked_y))
            else:
                self.loop.call_soon_threadsafe(self.data_queue.put_nowait, ("switch"))


    def start_monitoring(self):
        """Runs detection in a background thread."""
        if not self.running:
            self.running = True
            self.listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
            self.listener.start()
            print("Monitoring started...")


    def stop_monitoring(self):
        """Stops the monitoring loop."""
        self.running = False
        if self.listener:
            self.listener.stop()  
        print("Monitoring stopped.")


    def on_mouse_move(self, x, y):
        if self.is_server:
            if not self.block_mouse:
                print(f"Mouse moved to: {x}, {y}")  
                self.locked_x = x
                self.locked_y = y
            else:
                print(f"x:{x},y:{y}")
                delta_x, delta_y = self.cursor_tracker.delta_x_and_y(self.locked_x,self.locked_y,x,y)
                if abs(delta_x) > 1 or abs(delta_y) > 1:
                    self.loop.call_soon_threadsafe(self.data_queue.put_nowait, ("mouse_move", delta_x, delta_y))
            
        velocity_x, velocity_y = self.cursor_tracker.get_velocity(x, y)
        self.screen_edge_detector.detect_moving_to_edge(x, y, velocity_x, velocity_y)
    

    def on_mouse_click(self, x, y, button, pressed):
        if self.block_mouse and pressed:  # Optional: Only register when button is pressed
            self.loop.call_soon_threadsafe(self.data_queue.put_nowait, ("mouse_click",button))



    def on_switch_monitor(self):
        self.mouse_lib.EnableMouse(self.block_mouse)
        self.block_mouse = not self.block_mouse
        print(self.block_mouse)
