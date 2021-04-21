import http.server
import socketserver
import socket

PORT = 63654
Handler = http.server.SimpleHTTPRequestHandler
h_name = socket.gethostname()
IPaddr = str(socket.gethostbyname(h_name))

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at " + IPaddr + ":" + str(PORT))
    httpd.serve_forever()
