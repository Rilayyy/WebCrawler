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
        
        request_line = f"{method} {path} HTTP/1.1\r\n"
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

        self.client.send(request_line.encode('utf-8'))

    def recive_response(self):

        data = self.client.recv(4096)
        decoded_data = data.decode('utf-8')
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

