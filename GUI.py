import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import os
import subprocess
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

tray_icon = None  

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unavailable"

def create_tray_icon():
    global tray_icon
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle([16, 16, 48, 48], fill=(0, 255, 0))

    def on_quit(icon, item):
        icon.stop()

    tray_icon = Icon("ClientConnected", image, "Connected to Server", menu=Menu(MenuItem("Quit", on_quit)))
    tray_icon.run()  # Blocking call

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Menu")
        self.geometry("600x400")
        self.resizable(True, True)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (MainPage, ServerPage, ClientPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(MainPage)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

    def on_close(self):
        for config_file in ["server_config.json", "client_config.json"]:
            if os.path.exists(config_file):
                try:
                    os.remove(config_file)
                    print(f"[*] {config_file} deleted.")
                except Exception as e:
                    print(f"[!] Failed to delete {config_file}: {e}")
        self.destroy()

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Choose Mode", font=("Arial", 18)).pack(pady=20)
        tk.Button(self, text="Server", height=2, command=lambda: controller.show_frame(ServerPage), font=("Arial", 14)).pack(pady=10, padx=40, fill="x")
        tk.Button(self, text="Client", height=2, command=lambda: controller.show_frame(ClientPage), font=("Arial", 14)).pack(pady=10, padx=40, fill="x")

class ServerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Server Configuration", font=("Arial", 16)).pack(pady=10)

        self.direction_var = tk.StringVar(value="LEFT")
        directions = ["LEFT", "RIGHT", "UP", "DOWN"]
        ttk.Label(self, text="Select Direction").pack(pady=(10, 2))
        ttk.OptionMenu(self, self.direction_var, directions[0], *directions).pack(fill="x", padx=40)

        tk.Button(self, text="Start", command=self.start_server, font=("Arial", 14), height=2).pack(pady=20, padx=40, fill="x")

        self.stop_button = tk.Button(self, text="Stop", command=self.stop_server, state="disabled", font=("Arial", 14), height=2)
        self.stop_button.pack(pady=10, padx=40, fill="x")

        self.ip_label = tk.Label(self, text="", font=("Courier", 12))
        self.ip_label.pack(pady=10)

        tk.Button(self, text="← Back", command=lambda: controller.show_frame(MainPage), font=("Arial", 14), height=2).pack(pady=10, padx=40, fill="x")

        self.server_process = None

    def start_server(self):
        config = {
            "host": "0.0.0.0",
            "port": 5555,
            "direction": self.direction_var.get()
        }
        with open("server_config.json", "w") as f:
            json.dump(config, f, indent=4)

        ip = get_local_ip()
        self.ip_label.config(text=f"Your IP: {ip}")
        self.server_process = subprocess.Popen(["python", "-m", "network.server"])  
        self.stop_button.config(state="normal") 

    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.stop_button.config(state="disabled")
            self.ip_label.config(text="Server Stopped")
            print("[*] Server stopped.")
        else:
            messagebox.showerror("Error", "Server is not running!")

class ClientPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Client Configuration", font=("Arial", 16)).pack(pady=10)

        self.ip_entry = tk.Entry(self, font=("Arial", 14), width=25)
        self.ip_entry.pack(pady=10)
        self.ip_entry.insert(0, "Enter Server IP")
        self.ip_entry.bind("<FocusIn>", self.on_focus_in)
        self.ip_entry.bind("<FocusOut>", self.on_focus_out)

        tk.Button(self, text="Connect", command=self.connect_client, font=("Arial", 14), height=2).pack(pady=20, padx=40, fill="x")
        tk.Button(self, text="← Back", command=lambda: controller.show_frame(MainPage), font=("Arial", 14), height=2).pack(pady=10, padx=40, fill="x")

    def on_focus_in(self, event):
        if self.ip_entry.get() == "Enter Server IP":
            self.ip_entry.delete(0, tk.END)

    def on_focus_out(self, event):
        if self.ip_entry.get() == "":
            self.ip_entry.insert(0, "Enter Server IP")

    def connect_client(self):
        global tray_icon
        server_ip = self.ip_entry.get()
        if server_ip and server_ip != "Enter Server IP":
            client_config = {
                "host": server_ip,
                "port": 5555
            }
            with open("client_config.json", "w") as f:
                json.dump(client_config, f, indent=4)

            print(f"[*] Client will attempt to connect to server at {server_ip}")

            client_proc = subprocess.Popen(["python", "-m", "network.client"])
            threading.Thread(target=create_tray_icon, daemon=True).start()
            threading.Thread(target=self.monitor_client, args=(client_proc,), daemon=True).start()
        else:
            messagebox.showwarning("Invalid IP", "Please enter a valid server IP.")

    def monitor_client(self, process):
        global tray_icon
        process.wait()  # Blocks until client exits
        print("[*] Client disconnected.")
        if tray_icon:
            tray_icon.stop()
            tray_icon = None

if __name__ == "__main__":
    app = App()
    app.mainloop()
