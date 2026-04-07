#!/usr/bin/env python3

import socket
import ssl

class HttpClient: 
    def __init__(self): 

        self.server = "fakebook.khoury.northeastern.edu"
        self.port = 443
        self.cookie_jar = {}
        self.ssl_context = ssl.create_default_context()


    def connect(self):

        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        ssock = self.ssl_context.wrap_socket(mysocket, server_hostname=self.server)

        self.client = ssock

        self.client.connect((self.server, self.port))

    def send_request(self, method, path, body = None):
        
        request = f"{method} {path} HTTP/1.1\r\n"
        request += f"Host: {self.server}\r\n"
        request += "Connection: close\r\n"
        request += "User-Agent: CS4700-Crawler/1.0\r\n"
        
        # Add Referer for POST requests (Django CSRF requirement)
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

        print(f"Sending request: {method} {path}")
        self.client.send(request.encode('utf-8'))

    def recive_response(self):

        # Receive all data until connection closes
        data = b""
        while True:
            chunk = self.client.recv(4096)
            if not chunk:
                break
            data += chunk
        
        decoded_data = data.decode('utf-8')
        
        # Parse HTTP response
        header_end = decoded_data.find("\r\n\r\n")
        if header_end == -1:
            print("No headers found in response")
            return None
            
        headers = decoded_data[:header_end]
        body = decoded_data[header_end + 4:]
        
        # Parse status line
        lines = headers.split("\r\n")
        status_line = lines[0]
        parts = status_line.split(" ")
        if len(parts) >= 2:
            status_code = parts[1]
        else:
            status_code = "Unknown"
        
        print(f"Status Code: {status_code}")
        print(f"All headers: {headers}")
        
        # Extract cookies and location
        location = None
        for line in lines[1:]:
            if line.startswith("set-cookie:"):
                cookie_data = line[11:].strip()
                if "=" in cookie_data:
                    cookie_name, cookie_value = cookie_data.split("=", 1)
                    cookie_value = cookie_value.split(";")[0].strip()
                    self.cookie_jar[cookie_name] = cookie_value
                    print(f"Cookie extracted: {cookie_name}={cookie_value}")
            elif line.startswith("Location:"):
                location = line[10:].strip()
                print(f"Redirect location: {location}")
        
        # Handle chunked encoding
        if "Transfer-Encoding: chunked" in headers:
            body = self.decode_chunked(body)
        
        print(f"Body length: {len(body)} characters")
        
        return {
            'status_code': status_code,
            'headers': headers,
            'body': body,
            'location': location
        }

    def decode_chunked(self, body):
        clean_html = ""
        cursor = 0

        while True: 

            newline = body.find("\r\n", cursor)

            chunk_size = int(body[cursor:newline], 16)
            cursor = newline + 2

            if chunk_size == 0:
                break

            clean_html += body[cursor:cursor+chunk_size]
            cursor += chunk_size

            cursor += 2

        return clean_html

    if __name__ == "__main__":
        client = HttpClient()
        client.connect()
        client.send_request("GET", "/fakebook/")
        client.recive_response()

