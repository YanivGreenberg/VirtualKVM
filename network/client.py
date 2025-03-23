# client.py (asyncio)
import asyncio
from pynput.mouse import Controller, Button
from position import  get_full_screen_roi
import json
from edge_detector import Direction, ScreenEdgeDetector
from monitor import ScreenCursorMonitor


class Client:
    def __init__(self):
        self.mouse_controller = Controller()
        self.border = None
        self.mouse_tracker = None
        self.region = get_full_screen_roi()
        self.server_connected = False
        self.data_queue = asyncio.Queue()

    async def connect(self, host='192.168.1.111', port=5555):
        try:
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

async def main():
    client = Client()
    await client.connect()

if __name__ == "__main__":
    asyncio.run(main())