import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import os
import subprocess


def get_local_ip():
    try:
        # Gets local IP using socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unavailable"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Menu")
        self.geometry("600x400")  # Increased window size
        self.resizable(True, True)  # Allow window resizing

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (MainPage, ServerPage, ClientPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(MainPage)

        # Hook close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

    def on_close(self):
        if os.path.exists("server_config.json"):
            try:
                os.remove("server_config.json")
                print("[*] config.json deleted.")
            except Exception as e:
                print(f"[!] Failed to delete config.json: {e}")
        elif os.path.exists("client_config.json"):
            try:
                os.remove("client_config.json")
                print("[*] config.json deleted.")
            except Exception as e:
                print(f"[!] Failed to delete config.json: {e}")
        self.destroy()


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Choose Mode", font=("Arial", 18)).pack(pady=20)

        # Adjust buttons to be slightly bigger but not stretched too wide
        tk.Button(self, text="Server", height=2, command=lambda: controller.show_frame(ServerPage), font=("Arial", 14)).pack(pady=10, padx=40, fill="x")
        tk.Button(self, text="Client", height=2, command=lambda: controller.show_frame(ClientPage), font=("Arial", 14)).pack(pady=10, padx=40, fill="x")


class ServerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Server Configuration", font=("Arial", 16)).pack(pady=10)

        # Dropdown for direction
        self.direction_var = tk.StringVar(value="LEFT")
        directions = ["LEFT", "RIGHT", "UP", "DOWN"]
        ttk.Label(self, text="Select Direction").pack(pady=(10, 2))
        ttk.OptionMenu(self, self.direction_var, directions[0], *directions).pack(fill="x", padx=40)

        # Start button
        tk.Button(self, text="Start", command=self.start_server, font=("Arial", 14), height=2).pack(pady=20, padx=40, fill="x")

        self.stop_button = tk.Button(self, text="Stop", command=self.stop_server, state="disabled", font=("Arial", 14), height=2)
        self.stop_button.pack(pady=10, padx=40, fill="x")

        # Label to show IP after pressing start
        self.ip_label = tk.Label(self, text="", font=("Courier", 12))
        self.ip_label.pack(pady=10)

        # Back to main menu
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
            self.server_process.terminate()  # Gracefully terminate the server
            self.server_process.wait()  # Wait for the process to terminate

            # Disable stop button and update the label
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

        # Entry for the server IP
        self.ip_entry = tk.Entry(self, font=("Arial", 14), width=25)
        self.ip_entry.pack(pady=10)
        self.ip_entry.insert(0, "Enter Server IP")  # Placeholder text

        # Remove placeholder text when the user clicks the Entry box
        self.ip_entry.bind("<FocusIn>", self.on_focus_in)
        self.ip_entry.bind("<FocusOut>", self.on_focus_out)

        # Connect button
        tk.Button(self, text="Connect", command=self.connect_client, font=("Arial", 14), height=2).pack(pady=20, padx=40, fill="x")

        # Back to main menu
        tk.Button(self, text="← Back", command=lambda: controller.show_frame(MainPage), font=("Arial", 14), height=2).pack(pady=10, padx=40, fill="x")

    def on_focus_in(self, event):
        if self.ip_entry.get() == "Enter Server IP":
            self.ip_entry.delete(0, tk.END)  # Clear the placeholder when clicked

    def on_focus_out(self, event):
        if self.ip_entry.get() == "":
            self.ip_entry.insert(0, "Enter Server IP")  # Reset placeholder text if no input

    def connect_client(self):
        server_ip = self.ip_entry.get()
        if server_ip and server_ip != "Enter Server IP":
            client_config = {
                "host": server_ip,
                "port": 5555
            }

            with open("client_config.json", "w") as f:
                json.dump(client_config, f, indent=4)

            print(f"[*] Client will attempt to connect to server at {server_ip}")

            # Here you can run client code or subprocess to connect to the server if needed
            subprocess.Popen(["python", "-m", "network.client"])
        else:
            messagebox.showwarning("Invalid IP", "Please enter a valid server IP.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
