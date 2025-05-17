
import socket
import json
import os 

SERVER_HOST = '127.0.0.1'  
SERVER_PORT = 65432        # The port used by the server

def get_ip_from_user():
    while True:
        user_input = input("Enter IPv4 address or 'file <filepath>' (or 'exit' to quit): ").strip()
        if user_input.lower() == 'exit':
            return None
        if user_input.lower().startswith("file "):
            filepath = user_input[5:].strip()
            
            filepath = filepath.strip('\'"')
            if not os.path.exists(filepath):
                print(f"Error: File '{filepath}' not found.")
                continue
            try:
                with open(filepath, 'r') as f:
                    ip_address = f.readline().strip() 
                    if not ip_address:
                        print(f"Error: File '{filepath}' is empty or first line is empty.")
                        continue
                    print(f"Read IP '{ip_address}' from file '{filepath}'.")
                    return ip_address
            except Exception as e:
                print(f"Error reading file '{filepath}': {e}")
                continue
        elif user_input:
            return user_input
        else:
            print("Input cannot be empty.")

def run_client():
    while True:
        ip_to_validate = get_ip_from_user()
        if not ip_to_validate:
            print("Exiting client.")
            break

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                print(f"Attempting to connect to server {SERVER_HOST}:{SERVER_PORT}...")
                s.connect((SERVER_HOST, SERVER_PORT))
                print(f"Connected to server.")

                s.sendall(ip_to_validate.encode('utf-8'))
                print(f"Sent IP for validation: {ip_to_validate}")

                data = s.recv(4096) 
                response = json.loads(data.decode('utf-8'))

                print("\n--- Server Response ---")
                print(f"IP Checked: {response.get('ip')}")
                print(f"Status: {response.get('status')}")
                if response.get('reasons'):
                    print("Reasons:")
                    for reason in response.get('reasons'):
                        print(f"  - {reason}")
                print("-----------------------\n")

            except ConnectionRefusedError:
                print(f"Connection refused. Is the server running at {SERVER_HOST}:{SERVER_PORT}?")
                break 
            except json.JSONDecodeError:
                print("Error: Could not decode JSON response from server.")
            except socket.error as e:
                print(f"Socket error: {e}")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break 

if __name__ == "__main__":
    run_client()