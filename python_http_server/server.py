import http.server
import socketserver
import os
import socket
import threading
import mimetypes
from datetime import datetime

# --- Configuration ---
SERVER_HOST = '127.0.0.1'  # Listen on localhost
SERVER_PORT = 8000         # Port to listen on
WEB_ROOT = os.path.abspath('webroot')  # Absolute path to the web root directory
BUFFER_SIZE = 4096         # Size of buffer for receiving data

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            # Serve the homepage (index.html)
            super().do_GET()
        elif self.path == "/files.html":
            # Serve the file list page
            self.serve_file_list()
        else:
            # Let the parent class handle static file serving
            super().do_GET()

    def serve_file_list(self):
        """Generates and serves a page listing all files in the webroot."""
        try:
            file_list = os.listdir(WEB_ROOT)
            links = []
            for fname in file_list:
                # Skip hidden files
                if not fname.startswith("."):
                    links.append(f"<li><a href='/{fname}'>{fname}</a></li>")
            content = f"""
                <html>
                <head><title>File List</title></head>
                <body>
                    <h2>Available Files</h2>
                    <ul>{''.join(links)}</ul>
                    <a href="/">Back to Home</a>
                </body>
                </html>
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        except OSError:
            self.send_error(404, "Directory not found")

os.chdir(WEB_ROOT)
Handler = MyHandler

# Ensure the webroot directory exists
if not os.path.exists(WEB_ROOT):
    print(f"[!] Error: Web root directory '{WEB_ROOT}' not found.")
    print("[*] Please create the 'webroot' directory and place your static files (like index.html) inside it.")
    exit(1)
elif not os.path.isdir(WEB_ROOT):
    print(f"[!] Error: '{WEB_ROOT}' exists but is not a directory.")
    exit(1)

def get_current_datetime_rfc1123():
    """Returns the current date and time formatted according to RFC 1123 (HTTP Date header standard)."""
    now = datetime.utcnow()
    return now.strftime('%a, %d %b %Y %H:%M:%S GMT')

def handle_client_connection(client_sock, client_addr):
    """Handles connection for a single client."""
    print(f"[+] Accepted connection from {client_addr[0]}:{client_addr[1]}")
    try:
        # Receive data from the client
        request_data = client_sock.recv(BUFFER_SIZE)
        if not request_data:
            print(f"[-] Client {client_addr} disconnected without sending data.")
            return # Exit the handler function

        # Decode bytes to string using UTF-8 (standard for HTTP text)
        try:
            request_text = request_data.decode('utf-8')
        except UnicodeDecodeError:
            print(f"[!] Failed to decode request from {client_addr} (likely not UTF-8). Sending 400.")
            status_code, status_text = 400, "Bad Request"
            response_body = b"<h1>400 Bad Request (Invalid Encoding)</h1>"
            content_type = "text/html"
            # Jump directly to sending the response
            raise ConnectionAbortedError("Sending 400 due to bad encoding") # Use specific exception to jump

        # --- Parse Request ---
        print(f"\n--- Request from {client_addr} ---")
        try:
            first_line = request_text.splitlines()[0]
            print(first_line)
            print("--------------------------\n")
            method, raw_path, version = first_line.split()
        except (ValueError, IndexError):
            print("[!] Malformed or incomplete request line. Sending 400.")
            status_code, status_text = 400, "Bad Request"
            response_body = b"<h1>400 Bad Request</h1>"
            content_type = "text/html"
            # Jump directly to sending the response
            raise ConnectionAbortedError("Sending 400 due to bad request line")

        print(f"[*] Method: {method}, Path: {raw_path}, Version: {version}")

        # --- Handle Request (Only GET is supported) ---
        if method == "GET":
            # Security: Prevent accessing files outside WEB_ROOT
            # Normalize path, remove leading '/'
            relative_path = os.path.normpath(raw_path.lstrip('/'))

            # Check for path traversal attempts
            if relative_path.startswith('..') or os.path.isabs(relative_path):
                print(f"[!] Forbidden path request: {raw_path}. Sending 403.")
                status_code, status_text = 403, "Forbidden"
                response_body = b"<h1>403 Forbidden</h1>"
                content_type = "text/html"
            else:
                # Construct the full path safely within the web root
                requested_file_path = os.path.join(WEB_ROOT, relative_path)
                print(f"[*] Mapped path to: {requested_file_path}")

                # Default to index.html if a directory is requested
                if os.path.isdir(requested_file_path):
                    index_path = os.path.join(requested_file_path, 'index.html')
                    if os.path.isfile(index_path):
                        requested_file_path = index_path
                        print(f"[*] Serving index.html for directory request: {raw_path}")
                    else:
                        # No index.html in directory - Forbidden
                        print(f"[!] No index.html found for directory: {raw_path}. Sending 403.")
                        status_code, status_text = 403, "Forbidden"
                        response_body = b"<h1>403 Forbidden - Directory Listing Denied</h1>"
                        content_type = "text/html"
                        requested_file_path = None # Signal not to proceed with file serving logic

                # Check if the final path points to an existing file
                if requested_file_path and os.path.isfile(requested_file_path):
                    try:
                        print(f"[*] Serving file: {requested_file_path}")
                        # File exists, prepare 200 OK response
                        status_code, status_text = 200, "OK"

                        # Guess the MIME type (e.g., 'text/html', 'image/jpeg')
                        content_type, _ = mimetypes.guess_type(requested_file_path)
                        if content_type is None:
                            content_type = 'application/octet-stream' # Default binary type
                        print(f"[*] Content-Type: {content_type}")

                        # Read the file content IN BINARY MODE
                        with open(requested_file_path, 'rb') as f:
                            response_body = f.read()

                    except IOError as e:
                         print(f"[!] I/O Error reading file {requested_file_path}: {e}. Sending 500.")
                         status_code, status_text = 500, "Internal Server Error"
                         response_body = b"<h1>500 Internal Server Error</h1>"
                         content_type = "text/html"

                # Handle file not found after resolving path/index.html
                elif requested_file_path:
                    print(f"[!] File not found: {requested_file_path}. Sending 404.")
                    status_code, status_text = 404, "Not Found"
                    response_body = b"<h1>404 Not Found</h1>"
                    content_type = "text/html"

        else: # Method not GET
            print(f"[!] Unsupported method '{method}'. Sending 405.")
            status_code, status_text = 405, "Method Not Allowed"
            response_body = b"<h1>405 Method Not Allowed</h1>"
            content_type = "text/plain" # Often text/html is used for error pages too

    except ConnectionAbortedError as cae:
         # This is used internally to jump to the response sending for 400 errors
         print(f"[*] Jumping to send response due to: {cae}")
         # Status code, body, content type are already set before raising
         pass
    except Exception as e:
        # Catch any other unexpected errors during request processing
        print(f"[!] Internal Server Error handling request from {client_addr}: {e}")
        status_code, status_text = 500, "Internal Server Error"
        response_body = b"<h1>500 Internal Server Error</h1>"
        content_type = "text/html"

    # --- Construct and Send Response ---
    try:
        response_headers = f"HTTP/1.1 {status_code} {status_text}\r\n"
        response_headers += f"Server: SimplePythonHTTPServer\r\n"
        response_headers += f"Date: {get_current_datetime_rfc1123()}\r\n"
        response_headers += f"Content-Type: {content_type}\r\n"
        response_headers += f"Content-Length: {len(response_body)}\r\n" # Length of bytes body
        response_headers += f"Connection: close\r\n" # Tell client we will close connection
        response_headers += "\r\n" # Blank line signifies end of headers

        # Send headers (as bytes)
        client_sock.sendall(response_headers.encode('utf-8'))
        # Send body (already bytes)
        client_sock.sendall(response_body)

        print(f"[*] Response {status_code} sent to {client_addr}")

    except socket.error as sock_err:
        print(f"[!] Socket Error sending response to {client_addr}: {sock_err}")
    except Exception as e:
        print(f"[!] Error sending response to {client_addr}: {e}")

    finally:
        # Make sure the connection to this specific client is closed
        print(f"[-] Closing connection to {client_addr[0]}:{client_addr[1]}")
        client_sock.close()


# --- Main Server Setup and Loop ---
def main():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow reusing the address (prevents "Address already in use" error on quick restarts)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Bind the socket to the address and port
        server_socket.bind((SERVER_HOST, SERVER_PORT))
    except OSError as e:
        print(f"[!] Error binding to {SERVER_HOST}:{SERVER_PORT} - {e}")
        print("[*] Is the port already in use? Exiting.")
        exit(1)

    # Start listening for incoming connections (allow reasonable backlog)
    server_socket.listen(10) # Increased backlog slightly
    print(f"[*] Server listening on http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"[*] Serving files from: {WEB_ROOT}")
    print("[*] Press Ctrl+C to stop the server")

    try:
        while True:
            # Wait for an incoming connection
            client_sock, client_addr = server_socket.accept()

            # Handle the client connection in a new thread to handle concurrency
            client_thread = threading.Thread(target=handle_client_connection, args=(client_sock, client_addr))
            client_thread.start()

    except KeyboardInterrupt:
        print("\n[*] Shutting down the server...")
    finally:
        server_socket.close()


# Run the server
if __name__ == "__main__":
    main()
