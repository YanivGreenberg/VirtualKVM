# client.py (asyncio)
import asyncio
from pynput.mouse import Controller
from position import  get_full_screen_roi
import json


class Client:
    def __init__(self):
        self.mouse_controller = Controller()

    async def connect(self, host='192.168.1.111', port=5555):
        try:
            self.reader, self.writer = await asyncio.open_connection(host, port)
            print(f"[*] Connected to server at {host}:{port}")
            message = f"regin:{json.dumps(get_full_screen_roi())}\n".encode()
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
                if button == "left":
                    self.mouse_controller.click(self.mouse_controller.Button.left)
                elif button == "right":
                    self.mouse_controller.click(self.mouse_controller.Button.right)
                elif button == "middle":
                    self.mouse_controller.click(self.mouse_controller.Button.middle)
                else:
                    print("Invalid button click data from server.")
            except Exception as e:
                print(f"Error clicking mouse: {e}")

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