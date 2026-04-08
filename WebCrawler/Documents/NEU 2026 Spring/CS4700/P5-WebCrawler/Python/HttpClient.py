#!/usr/bin/env python3

import socket
import ssl

class HttpClient:
    """
    HTTP/1.1 client with TLS support and cookie management.
    
    Implements HTTP protocol from scratch without using forbidden libraries.
    Features:
    - TLS/SSL connection wrapping for HTTPS
    - HTTP/1.1 request formatting with required headers
    - Response parsing and status code handling
    - Cookie extraction and management for sessions
    - Chunked transfer encoding decoding
    """
    
    def __init__(self):
        """Initialize HTTP client with default Fakebook settings."""
        self.server = "fakebook.khoury.northeastern.edu"  
        self.port = 443                             
        self.cookie_jar = {}                              
        self.ssl_context = ssl.create_default_context()  

    def connect(self):
        """
        Establish TLS connection to the HTTPS server.
        
        Creates a TCP socket, wraps it with SSL/TLS, and connects to the server.
        This implements the HTTP over TLS over TCP stack required by HTTPS.
        """
        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        ssock = self.ssl_context.wrap_socket(mysocket, server_hostname=self.server)
        
        self.client = ssock
        
        self.client.connect((self.server, self.port))

    def send_request(self, method, path, body=None):
        """
        Send HTTP/1.1 request to the server.
        
        Implements HTTP/1.1 protocol with required headers including:
        - Host header
        - Connection: close 
        - User-Agent for identification
        - Referer for POST requests 
        - Cookie header for session management
        - Content-Type and Content-Length for POST requests
        
        Args:
            method: HTTP method (GET, POST)
            path: Request path 
            body: Request body for POST requests
        """
        request = f"{method} {path} HTTP/1.1\r\n"
        
        request += f"Host: {self.server}\r\n"
        request += "Connection: close\r\n"
        request += "User-Agent: CS4700-Crawler/1.0\r\n"
        
        if method == "POST":
            request += f"Referer: https://{self.server}/accounts/login/\r\n"

        if self.cookie_jar != {}:
            cookie_strings = []
            for key, value in self.cookie_jar.items():
                cookie_strings.append(f"{key}={value}")
            request += f"Cookie: {'; '.join(cookie_strings)}\r\n"

        if body: 
            request += f"Content-Length: {len(body)}\r\n"
            request += "Content-Type: application/x-www-form-urlencoded\r\n"

        request += "\r\n"

        if body:
            request += body

        self.client.send(request.encode('utf-8'))

    def recive_response(self):
        """
        Receive and parse HTTP response from the server.
        
        Handles complete HTTP response parsing including:
        - Status line extraction
        - Header parsing
        - Cookie extraction from Set-Cookie headers
        - Location header extraction for redirects
        - Chunked transfer encoding decoding
        - Body content extraction
        
        Returns:
            dict: Parsed response with keys:
                - status_code: HTTP status code (str)
                - headers: Raw headers (str)
                - body: Response body (str)
                - location: Redirect URL if present (str or None)
        """
        data = b""
        while True:
            chunk = self.client.recv(4096)
            if not chunk:
                break
            data += chunk
        
        decoded_data = data.decode('utf-8')
        
        headers, _, body = decoded_data.partition('\r\n\r\n')
        
        lines = headers.split("\r\n")
        status_line = lines[0]
        parts = status_line.split(" ")
        if len(parts) >= 2:
            status_code = parts[1]
        else:
            status_code = "Unknown"
        
        location = None
        for line in lines[1:]:
            if line.startswith("set-cookie:"):
                cookie_data = line[11:].strip()
                if "=" in cookie_data:
                    cookie_name, cookie_value = cookie_data.split("=", 1)
                    cookie_value = cookie_value.split(";")[0].strip()
                    self.cookie_jar[cookie_name] = cookie_value
            elif line.startswith("Location:"):
                location = line[10:].strip()
        
        if "Transfer-Encoding: chunked" in headers:
            body = self.decode_chunked(body)
        
        return {
            'status_code': status_code,
            'headers': headers,
            'body': body,
            'location': location
        }

    def decode_chunked(self, body):
        """
        Decode HTTP chunked transfer encoding.
        
        HTTP/1.1 servers may send responses in chunks where each chunk
        starts with its size in hexadecimal followed by \r\n, then the data.
        The response ends with a 0-size chunk.
        
        Args:
            body: Chunked encoded response body
            
        Returns:
            str: Decoded response body
        """
        clean_html = ""
        cursor = 0
        
        while cursor < len(body):
            chunk_size_end = body.find('\r\n', cursor)
            if chunk_size_end == -1:
                break
                
            chunk_size_str = body[cursor:chunk_size_end]
            try:
                chunk_size = int(chunk_size_str, 16)
            except ValueError:
                break
                
            if chunk_size == 0:
                break  
                
            cursor = chunk_size_end + 2
            chunk_data = body[cursor:cursor + chunk_size]
            clean_html += chunk_data
            
            cursor += chunk_size + 2
            
        return clean_html

if __name__ == "__main__":
    client = HttpClient()
    client.connect()
    client.send_request("GET", "/fakebook/")
    client.recive_response()

