
import socket
import json
import threading
from UDP.SERVER.validator import validate_ipv4_syntax

HOST = '0.0.0.0'
PORT = 65432 

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    with conn:
        try:
            data = conn.recv(1024)
            if not data:
                print(f"[{addr}] No data, client likely closed connection gracefully before sending.")
                return 

            ip_to_validate = data.decode('utf-8')
            print(f"[{addr}] Received IP for validation: {ip_to_validate}")

            is_valid, reasons = validate_ipv4_syntax(ip_to_validate)

            response = {
                "ip": ip_to_validate,
                "status": "valid" if is_valid else "invalid",
                "reasons": reasons
            }
            conn.sendall(json.dumps(response).encode('utf-8'))
            print(f"[{addr}] Sent response: {response}")

        except ConnectionResetError:
            print(f"[{addr}] Connection reset by peer.")
        except socket.timeout:
            print(f"[{addr}] Socket timeout.")
        except Exception as e:
            print(f"[{addr}] Error: {e}")
        finally:
            print(f"[DISCONNECTED] {addr} disconnected.")
           

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind((HOST, PORT))
        s.listen()
        print(f"Multithreaded TCP Server listening on {HOST}:{PORT}")
        print("Waiting for connections...")

        try:
            while True: 
                conn, addr = s.accept()
                
                thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                thread.start()
                print(f"[ACTIVE CONNECTIONS] Approximately {threading.active_count() - 1} client(s).") # -1 for the main thread
        except KeyboardInterrupt:
            print("\nServer shutting down.")
        finally:
            print("Server has shut down.")


if __name__ == "__main__":
    run_server()