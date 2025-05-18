import streamlit as st
import socket
import json
import os
import sys
import subprocess

# Constants
DEFAULT_SERVER_HOST = '127.0.0.1'
DEFAULT_SERVER_PORT = 9999  # Assuming this is what was imported from UDP client

def send_and_receive(ip_address, server_host, server_port):
    """Send IP address to server and receive validation results using UDP"""
    try:
        # Create UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(10)  # Set timeout for receiving
            server_address = (server_host, server_port)
            
            # Send data - for UDP we use sendto instead of connect+sendall
            s.sendto(ip_address.encode('utf-8'), server_address)
            
            # For UDP, we typically receive a single datagram response
            try:
                data, _ = s.recvfrom(4096)  # UDP typically uses single datagram
                if not data:
                    return {"error": "No data received from server"}
                
                return json.loads(data.decode('utf-8'))
            except socket.timeout:
                return {"error": "Timeout waiting for server response"}
                
    except socket.timeout:
        return {"error": f"Timeout: Could not connect to server at {server_host}:{server_port}"}
    except ConnectionRefusedError:
        return {"error": f"Connection refused. Is the server running at {server_host}:{server_port}?"}
    except json.JSONDecodeError:
        return {"error": "Could not decode JSON response from server"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def validate_from_file(filepath):
    """Read IP address from file and return it"""
    try:
        with open(filepath, 'r') as f:
            ip_address = f.readline().strip()
        if not ip_address:
            return {"error": f"File '{os.path.basename(filepath)}' is empty or first line is empty"}
        return {"ip": ip_address}
    except Exception as e:
        return {"error": f"Error reading file '{os.path.basename(filepath)}': {str(e)}"}

def close_connection():
    """Function to exit the application properly"""
    # Clear session state data
    st.session_state.clear()
    # Use subprocess to kill the Streamlit process - this is the most reliable way to exit
    try:
        # Run the subprocess in a way that doesn't block
        subprocess.Popen(['pkill', '-f', 'streamlit run'])
    except Exception as e:
        st.error(f"Error closing application: {str(e)}")
        
    # Set a flag that we can check to stop rendering content
    st.session_state.exit_requested = True

def main():
    # Set page config for minimal look
    st.set_page_config(
        page_title="IPv4 Validator Client",
        page_icon="🌐",
        layout="centered"
    )
    
    # Initialize session state variables if they don't exist
    if 'response' not in st.session_state:
        st.session_state.response = None
    if 'exit_requested' not in st.session_state:
        st.session_state.exit_requested = False
        
    # Check if exit was requested
    if st.session_state.exit_requested:
        st.warning("Application is closing...")
        st.stop()
        return

    # App title with minimal styling
    st.title("IPv4 Validator Client")
    st.markdown("---")

    # Server configuration in a clean layout
    col1, col2 = st.columns(2)
    with col1:
        server_host = st.text_input("Server Host", value=DEFAULT_SERVER_HOST)
    with col2:
        server_port = st.number_input("Server Port", min_value=1, max_value=65535, value=DEFAULT_SERVER_PORT)

    # Input methods with tabs for a modern approach
    tab1, tab2 = st.tabs(["📝 Manual Input", "📂 From File"])
    
    with tab1:
        ip_address = st.text_input("Enter IPv4 Address", key="manual_ip")
        validate_manual = st.button("Validate IP", type="primary", use_container_width=True)
        
        if validate_manual:
            if not ip_address:
                st.error("Please enter an IPv4 address.")
            else:
                with st.spinner("Validating..."):
                    st.session_state.response = send_and_receive(ip_address, server_host, server_port)
    
    with tab2:
        uploaded_file = st.file_uploader("Choose a file with IP address", type=["txt"])
        validate_file = st.button("Load & Validate", type="primary", use_container_width=True)
        
        if validate_file and uploaded_file:
            # Save the uploaded file temporarily
            with open("temp_ip_file.txt", "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Read the IP from the file
            file_result = validate_from_file("temp_ip_file.txt")
            
            if "error" in file_result:
                st.error(file_result["error"])
            else:
                with st.spinner("Validating..."):
                    st.session_state.response = send_and_receive(file_result["ip"], server_host, server_port)
                    st.success(f"Loaded IP: {file_result['ip']}")
            
            # Clean up temp file
            if os.path.exists("temp_ip_file.txt"):
                os.remove("temp_ip_file.txt")

    # Display results
    st.markdown("---")
    st.subheader("Results")
    
    if st.session_state.response:
        if "error" in st.session_state.response:
            st.error(st.session_state.response["error"])
        else:
            result_container = st.container()
            with result_container:
                st.markdown("### Validation Results")
                
                # Create nicer looking result cards
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"IP Checked: {st.session_state.response.get('ip', 'N/A')}")
                with col2:
                    status = st.session_state.response.get('status', 'Unknown')
                    # Fix: Check for both "Valid" and "valid" case variations
                    if status.lower() == "valid":
                        # Further improved alignment to better match Streamlit's info box styling
                        st.markdown("""
                        <style>
                        .valid-status-container {
                            margin-top: -16px;
                        }
                        .valid-status {
                            background-color: #28a745;
                            color: white;
                            padding: 16px;
                            border-radius: 4px;
                            text-align: left;
                            font-weight: normal;
                            font-size: 14px;
                            border: 1px solid rgba(40, 167, 69, 0.2);
                            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        st.markdown(f'<div class="valid-status-container"><div class="valid-status">Status: {status}</div></div>', unsafe_allow_html=True)
                    else:
                        st.error(f"Status: {status}")
                
                if st.session_state.response.get('reasons'):
                    st.write("Reasons:")
                    for reason in st.session_state.response.get('reasons'):
                        st.markdown(f"- {reason}")

    # Close connection button at the bottom
    st.markdown("---")
    if st.button("Close Connection", type="secondary", use_container_width=True, key="close_button"):
        st.warning("Closing connection and exiting application...")
        st.balloons()  # Visual feedback that button was clicked
        # Add a small delay so the message is visible
        import time
        time.sleep(1)
        close_connection()
        st.stop()  # Stop execution immediately

if __name__ == "__main__":
    main()
