#!/usr/bin/env python3

import socket
import ssl

class HttpClient: 
    __init__(self): 

        self.server = "fakebook.khoury.northeastern.edu"
        self.port = 443
        self.cookie_jar = {}
        self.ssl_context = ssl.create_default_context()


    def connect(self):

        context = ssl.create_default_context()

        with socket.create_connection((self.server, self.port)) as sock:
            with context.wrap_socket(sock, server_hostname=self.server) as ssock:
                
                request = "GET /fakebook/ HTTP/1.1\r\nHost: fakebook.khoury.northeastern.edu\r\n\r\n"
                ssock.send(request.encode('ascii'))

                data = ssock.recv(4096)
                decoded_data = data.decode('ascii')
                # if length of data is zero, the server has closed the connection
                if len(data) == 0:
                    print("Response:\nSocket closed by %s" % self.server)
                elif "400" in decoded_data:
                    print(f"400 error response: {decoded_data}")
                elif "200" in decoded_data:
                    print(f"200 response. success")


    def send_request(self, method, path):
        
        request_line = f"{method} /fakebook/ HTTP/1.\r\n"
        request_line += f"Host: {self.server}\r\n"
        request_line += "Connection: keep-alive\r\n"

        if self.cookie_jar != {}:
            cookie_strings = []
            for key, value in self.cookie_jar.items():
                cookie_strings.append(f"{key}={value}")
            request_line += f"Cookie: {'; '.join(cookie_strings)}\r\n"

        if body: 
            request_line += f"Content-Length: {len(body)}\r\n"
            request_line += "Content-Type: application/x-www-form-urlencoded\r\n"

        request_line += "\r\n"

        if body:
            request_line += body

        self.client.send(request_line.encode('ascii'))

    def recive_response(self):

        data = self.client.recv(4096)
        decoded_data = data.decode('ascii')
        if len(data) == 0:
            print("Response:\nSocket closed by %s" % self.server)
        elif "400" in decoded_data:
            print(f"400 error response: {decoded_data}")
        elif "200" in decoded_data:
            print(f"200 response. success")

    def decode_chunked(self, body):

        clean_html = ""
        cursor = 0

        while True: 





