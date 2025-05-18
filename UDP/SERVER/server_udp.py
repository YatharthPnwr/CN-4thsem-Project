
import socket
import json
from validator import validate_ipv4_syntax

HOST = '127.0.0.1'
PORT = 65433 

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
        s.bind((HOST, PORT))
        print(f"UDP Server listening on {HOST}:{PORT}")

        while True:
            try:
                data, addr = s.recvfrom(1024) 
                ip_to_validate = data.decode('utf-8')
                print(f"Received IP from {addr}: {ip_to_validate}")

                is_valid, reasons = validate_ipv4_syntax(ip_to_validate)

                response = {
                    "ip": ip_to_validate,
                    "status": "valid" if is_valid else "invalid",
                    "reasons": reasons
                }
                s.sendto(json.dumps(response).encode('utf-8'), addr) 
                print(f"Sent response to {addr}: {response}")

            except Exception as e:
                print(f"Error handling request from {addr if 'addr' in locals() else 'unknown'}: {e}")

if __name__ == "__main__":
    run_server()