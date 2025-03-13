# server.py (asyncio)
import asyncio
from edge_detector import ScreenEdgeDetector
from monitor import ScreenCursorMonitor
from edge_detector import Direction
from position import  get_full_screen_roi, calculate_mouse_switch_position
import json

class Server:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = None
        self.data_queue = asyncio.Queue()  # Initialize the data queue
        self.region = get_full_screen_roi()
        self.mouse_tracker = ScreenCursorMonitor(self.region, Direction.LEFT, self.data_queue, True)
        ScreenEdgeDetector.attach(self.mouse_tracker)
        self.client_connected = False 
        self.client_regin = None


    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"[*] Accepted connection from {addr}")

        self.client_connected = True #set client connected.
        self.mouse_tracker.start_monitoring() #start monitoring.

        try:
            # First, explicitly read the initial client region message before entering the loop
            request = await reader.readline()
            if request:
                request = request.decode().strip()
                print(f"[*] Received initial request: {request}")
                await self.handle_request(request, writer)

            # Now start movement processing
            asyncio.create_task(self.send_movements(writer))

            while True:
                try:
                    request = await asyncio.wait_for(reader.readline(), timeout=0.1)
                    if request:
                        request = request.decode().strip()
                        print(f"[*] Received request: {request}")
                        await self.handle_request(request, writer)
                except asyncio.TimeoutError:
                    pass

        except ConnectionResetError:
            print(f"[*] Client {addr} disconnected.")
            await self.stop()
        except Exception as e:
            print(f"[*] Error: {e}")
            await self.stop()
        finally:
            writer.close()
            await writer.wait_closed()
            print(f"[*] Closed connection with {addr}")

    async def send_movements(self, writer):
        try:
            while self.client_connected:
                data = await self.mouse_tracker.data_queue.get() 
                data_type, *data_values = data
                if data_type == "mouse_move" and self.mouse_tracker.block_mouse:
                        dx, dy = data_values
                        print(f"Server sending: dx={dx}, dy={dy}") #added print statement
                        mouse_move_data = f"mouse_move:{dx},{dy}\n".encode()
                        writer.write(mouse_move_data)
                        await writer.drain()
                elif data_type == "mouse_set":
                    rx, ry = data_values
                    sx, sy = calculate_mouse_switch_position(rx,ry,self.region, self.client_regin)
                    mouse_set_data = f"mouse_set:{sx},{sy}\n".encode()
                    writer.write(mouse_set_data)
                    await writer.drain()
                #... handle other data types.
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in movement task: {e}")

    async def handle_request(self, request, writer):
        if request == "request_mouse_position":
            mouse_pos_data = f"mouse_set:100,200\n".encode()
            writer.write(mouse_pos_data)
            await writer.drain()

        elif request.startswith("regin:"):
            try:
                region_data = request[len("regin:"):]  # Extract region JSON
                self.client_regin = json.loads(region_data)  # Convert string to dictionary
                print(f"[*] Client region set: {self.client_regin}")
            except json.JSONDecodeError:
                print("[!] Error: Received invalid region data.")

        elif request == "switch":
            self.mouse_tracker.on_switch_monitor()
        else:
            print(f"[*] Unknown request: {request}")

    async def start(self):
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = self.server.sockets[0].getsockname()
        print(f"[*] Server listening on {addr}")

        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("[*] Server stopped.")
        if self.client_connected:
            self.mouse_tracker.stop_monitoring() #stop monitoring only if client was connected.

async def main():
    server = Server()
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n[*] Keyboard interrupt received. Stopping server...")
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())