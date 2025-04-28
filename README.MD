# Virtual KVM Switch

A virtual KVM (Keyboard, Mouse) switch that allows you to control multiple computers over a network with a single keyboard and mouse — no hardware required.

## Features
- Seamless control between multiple machines
- Cursor and screen change detection
- Lightweight background service
- Easy configuration and setup

## How It Works
The system uses a client-server model where one computer acts as the server (controller) and others act as clients. When the mouse cursor reaches the edge of the screen, control is transferred to the next machine.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Shganga/VirtualKVM.git
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Start the server on the main machine.
2. Start the client on each controlled machine (with the IP from the server).
3. Move your mouse across the screen edge to switch control!

## Configuration
- `server_config.json` and `client_config.json` will be made from the GUI when you start the server and the client
- Ensure all devices are on the same network.

## To compile the dll
```bash
 g++ -o mouse_control.dll mouse_control.cpp -shared
```
