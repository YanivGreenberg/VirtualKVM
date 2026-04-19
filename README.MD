# Virtual KVM Switch

A high-performance, software-based KVM (Keyboard, Video, Mouse) switch that allows you to seamlessly control multiple Windows computers over a local network using a single keyboard and mouse. 

## Features

* **Seamless Edge Switching:** Move your cursor to the edge of the server's screen to instantly transfer control to the client machine.
* **Dynamic Resolution Mapping:** Automatically calculates the bounding box of all connected monitors (`mss`) and proportionally maps cursor coordinates from the host's screen dimensions to the client's screen dimensions.
* **Low-Level Input Capture:** Utilizes a custom C++ DLL with Windows API hooks (`WH_MOUSE_LL`, `WH_KEYBOARD_LL`) to securely capture, block, and redirect OS-level mouse and keyboard events on the host.
* **Graphical User Interface (GUI):** A Tkinter dashboard to configure server directions, view local IPs, and connect clients. Automatically generates `server_config.json` and `client_config.json`.
* **System Tray Integration:** Runs quietly in the background with a system tray icon (`pystray`) for quick access and graceful background execution.

## Under the Hood: Architecture & Networking

This project relies on a highly optimized **Asynchronous Client-Server architecture**:

* **Asyncio & TCP Sockets:** The networking layer uses `asyncio` streams for non-blocking, concurrent event handling. The server implements `socket.TCP_NODELAY` and small buffer sizes (`SO_SNDBUF`) to ensure instantaneous packet delivery without Nagle's algorithm buffering delays.
* **Custom Event Protocol:** Inputs are serialized into a lightweight, string-based custom protocol (e.g., `mouse_move:dx,dy`, `key_pressed:code,bool,bool`, `mouse_scroll:delta`) and pushed to an `asyncio.Queue()` for immediate dispatch to the client.
* **Client-Side Simulation:** The client parses the incoming TCP stream and accurately reconstructs the input events on the target machine using `pynput` controllers.
* **Observer Pattern:** The edge detection logic (`edge_detector.py`) uses a Subject-Observer design pattern to monitor cursor velocity and coordinates, triggering network state changes only when an edge-breach threshold is met.

## Tech Stack

* **Python:** `asyncio`, `Tkinter`, `pynput`, `mss` (Screen dimensions), `ctypes` (C++ interop).
* **C++:** Compiled dynamic-link library (`mouse_control.dll`) for Windows API input hooking.

## Installation & Setup

### Prerequisites
* **Windows OS** (Required due to `win32api` and DLL dependencies)
* **Python 3.8+**

### 1. Clone the Repository
```bash
git clone https://github.com/Shganga/VirtualKVM.git
cd VirtualKVM
```

### 2. Set Up a Virtual Environment (Recommended)

Isolate the project dependencies to prevent conflicts with other Python packages:

```powershell
python -m venv venv
venv\Scripts\Activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Compile the DLL

To compile the C++ hooks into a self-contained DLL, use the following command (requires MinGW-w64 `g++`):

```bash
g++ -o mouse_control.dll mouse_control.cpp -shared -static -static-libgcc -static-libstdc++
```

## Usage

Launch the application via the GUI:

```bash
python GUI.py
```

### Setting up the Server (Main PC / Controller)

1.  Select **Server** from the Main Menu.
2.  Choose the screen edge (`LEFT`, `RIGHT`, `UP`, `DOWN`) that will trigger the switch.
3.  Click **Start**. The server will bind to `0.0.0.0:5555`.
4.  Note the "Your IP" displayed on the screen.

### Setting up the Client (Controlled PC)

1.  Run `GUI.py` on the second computer.
2.  Select **Client** from the Main Menu.
3.  Enter the IP address displayed on the Server.
4.  Click **Connect**. The app will minimize to your system tray.

To return control to the main PC, simply move the mouse back across the designated screen edge on the client machine.

## License

This project is open-source and available under the MIT License.
