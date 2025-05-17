# client_udp.py
import socket
import json
import os

print("--- client_udp.py script started ---") # ADD THIS LINE

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433 # UDP port

print("--- Constants defined ---") # ADD THIS LINE

def get_ip_from_user():
    
    while True:
        try:
            user_input = input("Enter IPv4 address or 'file <filepath>' (or 'exit' to quit): ").strip()
            print(f"--- User entered: {user_input} ---") 
        except Exception as e:
            print(f"--- ERROR IN input() or strip(): {e} ---")
            return None 
        if user_input.lower() == 'exit':
            return None
       
        if user_input.lower().startswith("file "):
            filepath = user_input[5:].strip().strip('\'"')
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
    print("--- run_client() called ---") 
    while True:
        ip_to_validate = get_ip_from_user()
        if not ip_to_validate:
            print("Exiting client.")
            break
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
            try:
                s.settimeout(5.0) 

                s.sendto(ip_to_validate.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
                print(f"Sent IP for validation to {SERVER_HOST}:{SERVER_PORT}: {ip_to_validate}")

                data, server_addr = s.recvfrom(4096) 
                response = json.loads(data.decode('utf-8'))

                print(f"\n--- Server Response from {server_addr} ---")
                print(f"IP Checked: {response.get('ip')}")
                print(f"Status: {response.get('status')}")
                if response.get('reasons'):
                    print("Reasons:")
                    for reason in response.get('reasons'):
                        print(f"  - {reason}")
                print("---------------------------------\n")

            except socket.timeout:
                print(f"Timeout: No response from server at {SERVER_HOST}:{SERVER_PORT} within 5 seconds.")
            except json.JSONDecodeError:
                print("Error: Could not decode JSON response from server.")
            except socket.error as e:
                print(f"Socket error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    print("--- Starting client execution (__name__ == '__main__') ---") 
    run_client()
    print("--- Client execution finished ---") 