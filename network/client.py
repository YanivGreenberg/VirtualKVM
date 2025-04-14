# client.py (asyncio)
import asyncio
from pynput.mouse import Controller as MouseController, Button
from position import  get_full_screen_roi
import json
from edge_detector import Direction, ScreenEdgeDetector
from monitor import ScreenCursorMonitor
from pynput.keyboard import Key, Controller as KeyboardController


class Client:
    def __init__(self):
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        self.border = None
        self.mouse_tracker = None
        self.region = get_full_screen_roi()
        self.server_connected = False
        self.data_queue = asyncio.Queue()

    async def connect(self,config):
        try:
            host = config.get('host')  
            port = config.get('port', 5555)  
            if not host:
                print("Error: No host (IP address) provided in config.")
                return
            
            self.reader, self.writer = await asyncio.open_connection(host, port)
            print(f"[*] Connected to server at {host}:{port}")
            self.server_connected = True
            message = f"region:{json.dumps(self.region)}\n".encode()
            self.writer.write(message)
            await self.writer.drain()

            await self.run()
        except ConnectionRefusedError:
            print(f"Error: Could not connect to {host}:{port}. Server may not be running.")
        except Exception as e:
            print(f"An error occurred during connection: {e}")
            await self.close()

    async def run(self):
        try:
            while True:
                data = await self.reader.readline()
                if not data:
                    print("Server disconnected.")
                    await self.close()
                    break
                message = data.decode().strip()
                print(f"Server says: {message}")
                self.handle_response(message)
        except ConnectionResetError:
            print("Server disconnected.")
            await self.close()
        except Exception as e:
            print(f"An error occurred during receive: {e}")
            await self.close()

    def handle_response(self, message):
        if message.startswith("mouse_move:"):
            try:
                data = message[len("mouse_move:"):]
                dx, dy = map(int, data.split(','))
                self.mouse_controller.move(dx, dy)
            except ValueError:
                print("Invalid mouse movement data from server.")
        elif message.startswith("mouse_set:"):
            try:
                data = message[len("mouse_set:"):]
                x, y = map(int, data.split(','))
                self.mouse_controller.position = (x, y)
            except ValueError:
                print("Invalid mouse position data from server.")
        elif message.startswith("mouse_click:"):
            try:
                button = message[len("mouse_click:"):]
                if button == '[1]': 
                    self.mouse_controller.click(Button.left)  
                elif button == '[2]':
                    self.mouse_controller.click(Button.right)  
                elif button == '[3]':
                    self.mouse_controller.click(Button.middle)
                else:
                    print("Invalid button click data from server.")
            except Exception as e:
                print(f"Error clicking mouse: {e}")
        elif message.startswith("key_pressed:"):
            try:
                data = message[len("key_pressed:"):]  # Extract data after the prefix
                key_str, is_pressed_str, is_upper_str = data.split(',')  # Split into two parts
                key = int(key_str.strip())  # Convert first part to int
                is_pressed = is_pressed_str.strip() == "True"
                is_upper = is_upper_str.strip() == "True"

                special_keys = {
                160: Key.shift_l,  # Shift
                161: Key.shift_r,
                162: Key.ctrl_l,   # Ctrl
                163: Key.ctrl_r,
                164: Key.alt_l,    # Alt
                165: Key.alt_r,
                9: Key.tab,     # Tab
                20: Key.caps_lock,  # Caps Lock
                27: Key.esc,    # Escape
                32: Key.space,  # Space
                13: Key.enter,  # Enter
                8: Key.backspace,  # Backspace
                }

                if key in special_keys:
                    key_char = special_keys[key]
                else:
                    key_char = chr(key).upper() if is_upper else chr(key).lower()

                if is_pressed:
                    self.keyboard_controller.press(key_char)
                else:
                    self.keyboard_controller.release(key_char)     

                    if is_pressed:
                        self.keyboard_controller.press(key_char)
                    else:
                        self.keyboard_controller.release(key_char)
            except Exception as e:
                print(f"Error pressing key: {e}")
            
        elif message.startswith("border:"):
            try:
                border = message[len("border:"):]
                print(f"border is: {border}")
                if border == "Direction.LEFT":
                    self.border = Direction.RIGHT
                elif border == "Direction.RIGHT":
                    self.border = Direction.LEFT
                elif border == "Direction.UP":
                    self.border = Direction.DOWN
                elif border == "Direction.DOWN":
                    self.border = Direction.UP
                if not self.mouse_tracker:
                    self.mouse_tracker = ScreenCursorMonitor(self.region, self.border, self.data_queue, False)
                    ScreenEdgeDetector.attach(self.mouse_tracker)
                    print(f"set tracker with border {self.border}")
                    self.mouse_tracker.start_monitoring()
                    asyncio.create_task(self.track_mouse_events())
            except Exception as e:
                print(f"border error: {e}")
                

    async def track_mouse_events(self):
        """ Monitors the mouse and sends messages only when needed. """
        if not self.mouse_tracker:
            return

        while self.server_connected:
            try:
                data = await self.mouse_tracker.data_queue.get()  
                data_type = data
                if data_type == "switch":
                    print(f"switching monitor")
                    message = f"switch\n".encode()
                    self.writer.write(message)
                    await self.writer.drain()

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in mouse tracking: {e}")


    async def close(self):
        if hasattr(self, 'writer') and self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        print("\nClient shutting down...")

async def run_client():
    config = load_config()
    client = Client()
    await client.connect(config)

def load_config(path="client_config.json"):
    with open(path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    asyncio.run(run_client())