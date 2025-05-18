
import socket
import json
from UDP.SERVER.validator import validate_ipv4_syntax 

HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 65432      # Port to listen on (non-privileged ports are > 1023)

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"TCP Server listening on {HOST}:{PORT}")

        while True: 
            conn, addr = s.accept() 
            with conn: 
                print(f"Connected by {addr}")
                try:
                    data = conn.recv(1024) 
                    if not data:
                        print(f"No data received from {addr}. Closing connection.")
                        continue 

                    ip_to_validate = data.decode('utf-8')
                    print(f"Received IP from client: {ip_to_validate}")

                    is_valid, reasons = validate_ipv4_syntax(ip_to_validate)

                    response = {
                        "ip": ip_to_validate,
                        "status": "valid" if is_valid else "invalid",
                        "reasons": reasons
                    }
                    conn.sendall(json.dumps(response).encode('utf-8'))
                    print(f"Sent response to {addr}: {response}")

                except ConnectionResetError:
                    print(f"Connection reset by {addr}")
                except Exception as e:
                    print(f"Error handling client {addr}: {e}")
                finally:
                    print(f"Closing connection with {addr}")
                   
if __name__ == "__main__":
    run_server()