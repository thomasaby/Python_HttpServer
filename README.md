# Simple Python HTTP Server (HTTP_server)

## Description

This project is a basic HTTP/1.1 server built from scratch in Python using the standard `socket` and `threading` libraries. The primary goal of this project was to learn the fundamentals of network programming, the HTTP protocol, concurrency, and low-level server operations without relying on high-level frameworks like Flask or Django.

It demonstrates how a server listens for connections, parses incoming HTTP requests, serves static files from a designated directory, handles multiple clients concurrently, and manages basic error conditions.

**Disclaimer:** This server is intended purely for educational purposes. It lacks many features and security considerations necessary for a production environment. **DO NOT USE IN PRODUCTION.**

## Features

* Handles HTTP `GET` requests.
* Serves static files (HTML, CSS, JS, images, etc.) from a `./webroot/` directory.
* Automatically serves `index.html` if the requested path is a directory containing it.
* Basic MIME type detection using the `mimetypes` module to set the `Content-Type` header.
* Basic security: Prevents directory traversal attacks trying to access files outside the `webroot` directory.
* Handles multiple client connections concurrently using Python's `threading` module (one thread per connection).
* Basic HTTP error handling:
    * `200 OK` for successful requests.
    * `403 Forbidden` for directory access attempts (if no `index.html`) or path traversal attempts.
    * `404 Not Found` for requests to non-existent files.
    * `405 Method Not Allowed` for methods other than `GET`.
    * Basic `400 Bad Request` for malformed request lines.
    * Basic `500 Internal Server Error` for unexpected server issues during request handling.
* Listens on a configurable host and port (defaults to `127.0.0.1:8080`).
* Graceful shutdown on `Ctrl+C`.

## Technology Stack

* **Language:** Python 3
* **Core Libraries:**
    * `socket` (for low-level networking)
    * `threading` (for concurrency)
    * `os` (for file system interactions and path manipulation)
    * `mimetypes` (for guessing file content types)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/thomasaby/Python_HttpServer.git](https://github.com/thomasaby/Python_HttpServer.git)
    cd HTTP_server
    ```

2.  **Ensure Python 3 is installed.**

## Usage

1.  **Navigate to the project directory:**
    ```bash
    cd HTTP_server
    ```

2.  **Create the web root directory:**
    ```bash
    mkdir webroot
    ```

3.  **Place static files** (e.g., `index.html`, `styles.css`, images) inside the `webroot` directory. An example `index.html` might be:
    ```html
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body><h1>Hello from HTTP_server!</h1></body>
    </html>
    ```

4.  **Run the server:**
    ```bash
    python server.py
    ```

5.  The terminal will output the address the server is listening on (e.g., `[*] Server listening on http://127.0.0.1:8080`).

6.  Open your web browser and navigate to the address shown (e.g., `http://127.0.0.1:8080` or `http://127.0.0.1:8080/your_file.html`).

7.  To stop the server, go back to the terminal where it's running and press `Ctrl+C`.

## Project Structure

HTTP_server/
├── server.py       # The main Python HTTP server script
├── webroot/        # Directory containing static files to be served
│   ├── index.html  # Example file served for directory requests
│   └── ...         # Other static files (CSS, JS, images, etc.)
└── README.md       # This documentation file

## Key Concepts Learned / Demonstrated

* **Socket Programming:** Binding, listening, accepting connections (`socket`).
* **TCP/IP Basics:** Understanding client-server interaction over TCP.
* **HTTP Protocol:** Parsing request lines (Method, Path, Version), constructing status lines and headers (`Content-Type`, `Content-Length`, `Connection`), understanding the request/response cycle.
* **Request Parsing:** Extracting essential information from raw HTTP request text.
* **File I/O:** Reading local files (especially in binary mode `rb`) to serve as response bodies.
* **MIME Types:** Identifying file types for the `Content-Type` header.
* **Concurrency:** Handling multiple clients simultaneously using `threading`.
* **Basic Error Handling:** Implementing HTTP status codes like 200, 403, 404, 405, 500.
* **Path Security:** Basic prevention of directory traversal (`os.path`, `normpath`).

## Limitations & Disclaimer (Important!)

* **Educational Use Only:** This server is **NOT** production-ready due to its simplicity and lack of robust security features.
* **Security:** Only implements very basic path traversal prevention. It is likely vulnerable to various other web security threats (e.g., certain types of denial-of-service, slowloris if not carefully managed, header injection vulnerabilities are not checked for, etc.). **HTTPS is not supported.**
* **HTTP Compliance:** Implements only a small subset of the HTTP/1.1 standard. Features like keep-alive connections, persistent connections, chunked transfer encoding, range requests, caching headers (`ETag`, `If-Modified-Since`), and handling complex header scenarios are missing.
* **Performance:** Concurrency via threading has limitations and overhead compared to asynchronous models (like `asyncio`) or pre-fork models, especially under heavy load.
* **Robustness:** Error handling is basic. It may crash or behave unexpectedly with highly malformed or malicious requests. Does not implement timeouts robustly.

## Future Improvements (Ideas)

* Implement support for other HTTP methods (e.g., `POST`, `HEAD`).
* Add support for HTTPS/TLS using the `ssl` module.
* Implement more robust request parsing (including headers).
* Add configuration options (e.g., via command-line arguments or a config file).
* Implement logging using the `logging` module.
* Explore asynchronous I/O using `asyncio` for potentially better performance.
* Add support for more HTTP features (caching, keep-alive, etc.).

## License

This project is open-source and available under the MIT License.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.

## Contact
For any questions, feel free to reach out via GitHub or email me at: thomasaby34@gmail.com