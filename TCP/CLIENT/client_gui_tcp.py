
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import socket
import json
import os

from UDP.CLIENT.client_gui_udp import DEFAULT_SERVER_PORT

DEFAULT_SERVER_HOST = '127.0.0.1' 

class IPValidatorClientGUI:
    def __init__(self, master):
        self.master = master
        master.title("IPv4 Validator Client (TCP)")

       
        config_frame = tk.Frame(master, padx=10, pady=10)
        config_frame.pack(fill=tk.X)

        tk.Label(config_frame, text="Server Host:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.host_entry = tk.Entry(config_frame, width=20)
        self.host_entry.insert(0, DEFAULT_SERVER_HOST)
        self.host_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(config_frame, text="Server Port:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.port_entry = tk.Entry(config_frame, width=7)
        self.port_entry.insert(0, str(self.new_method()))
        self.port_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        
        input_frame = tk.Frame(master, padx=10, pady=5)
        input_frame.pack(fill=tk.X)

        tk.Label(input_frame, text="Enter/Load IPv4:").pack(side=tk.LEFT, padx=5)
        self.ip_entry = tk.Entry(input_frame, width=30)
        self.ip_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

       
        button_frame = tk.Frame(master, padx=10, pady=5)
        button_frame.pack(fill=tk.X)

        self.validate_button = tk.Button(button_frame, text="Validate from Textbox", command=self.validate_from_textbox)
        self.validate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.file_button = tk.Button(button_frame, text="Load & Validate from File", command=self.validate_from_file)
        self.file_button.pack(side=tk.LEFT, padx=5, pady=5)

       
       
        result_frame = tk.Frame(master, padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(result_frame, text="Result:").pack(anchor=tk.W)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=12, width=60, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.config(state=tk.DISABLED)

    def new_method(self):
        return DEFAULT_SERVER_PORT

    def _send_and_receive(self, ip_address):
        server_host = self.host_entry.get().strip()
        if not server_host:
            messagebox.showerror("Config Error", "Server Host cannot be empty.")
            return None
        try:
            server_port_str = self.port_entry.get().strip()
            if not server_port_str:
                raise ValueError("Port cannot be empty.")
            server_port = int(server_port_str)
            if not (0 < server_port < 65536):
                raise ValueError("Port number out of range (1-65535).")
        except ValueError as e:
            messagebox.showerror("Config Error", f"Invalid port number: {e}")
            return None

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Attempting to validate: {ip_address}\nConnecting to {server_host}:{server_port}...\n")
        self.master.update_idletasks()

        response_data = None
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(10) 
                s.connect((server_host, server_port))
                s.sendall(ip_address.encode('utf-8'))
                data_chunks = []
                while True: 
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data_chunks.append(chunk)
                
                if not data_chunks:
                     self.result_text.insert(tk.END, "No data received from server.\n")
                     return None

                full_data = b"".join(data_chunks)
                response_data = json.loads(full_data.decode('utf-8'))
            except socket.timeout:
                messagebox.showerror("Connection Error", f"Timeout: Could not connect to or receive from server at {server_host}:{server_port}.")
                self.result_text.insert(tk.END, "Connection timed out.\n")
            except ConnectionRefusedError:
                messagebox.showerror("Connection Error", f"Connection refused. Is the server running at {server_host}:{server_port}?")
                self.result_text.insert(tk.END, "Connection refused.\n")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Could not decode JSON response from server.")
                self.result_text.insert(tk.END, "Failed to decode server response.\n")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                self.result_text.insert(tk.END, f"An error occurred: {e}\n")
        self.result_text.config(state=tk.DISABLED)
        return response_data

    def _display_response(self, response):
        self.result_text.config(state=tk.NORMAL)
        
        if response:
            self.result_text.insert(tk.END, f"\n--- Server Response ---\n")
            self.result_text.insert(tk.END, f"IP Checked: {response.get('ip')}\n")
            self.result_text.insert(tk.END, f"Status: {response.get('status')}\n")
            if response.get('reasons'):
                self.result_text.insert(tk.END, "Reasons:\n")
                for reason in response.get('reasons'):
                    self.result_text.insert(tk.END, f"  - {reason}\n")
            self.result_text.insert(tk.END, "-----------------------\n")
        else:
            self.result_text.insert(tk.END, "Failed to get a valid response or an error occurred.\n")
        self.result_text.config(state=tk.DISABLED)
        self.result_text.see(tk.END) 

    def validate_from_textbox(self):
        ip_address = self.ip_entry.get().strip()
        if not ip_address:
            messagebox.showwarning("Input Error", "Please enter an IPv4 address.")
            return
        response = self._send_and_receive(ip_address)
        self._display_response(response)

    def validate_from_file(self):
        filepath = filedialog.askopenfilename(
            title="Select IP Address File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                ip_address = f.readline().strip()
            if not ip_address:
                messagebox.showwarning("File Error", f"File '{os.path.basename(filepath)}' is empty or first line is empty.")
                return
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, ip_address)
            response = self._send_and_receive(ip_address)
            self._display_response(response)
        except Exception as e:
            messagebox.showerror("File Error", f"Error reading file '{os.path.basename(filepath)}': {e}")

if __name__ == "__main__":
    print("Attempting to create Tkinter root window...")
    root = tk.Tk()
    print("Tkinter root window created. Initializing GUI...")
    gui = IPValidatorClientGUI(root)
    print("GUI initialized. Starting mainloop...")
    root.mainloop()
    print("Mainloop has exited (window was closed).")