from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = 5000
data = b"A" * 10240 #Data, der sendes som svar til klienten (10240 bytes ≈ 10 KB)

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self): #Håndterer HTTP GET-requests
        self.send_response(200) #Returnerer en 200 OK statuskode, som fortæller at serveren har modtaget og forstået requesten
        self.send_header("Content-type", "text/plain") #Angiver at indholdet af svaret er almindelig tekst
        self.send_header("Content-Length", str(len(data)))
        self.end_headers() #Afslutter HTTP-headeren, så serveren kan begynde at sende selve svaret
        self.wfile.write(data) #Sender data som svar til klienten

    def log_message(self, format, *args):
        return  #Deaktiverer standard logning af HTTP-requests, så serveren ikke logger hver request til konsollen

#threading
def handle_client(connection, address):
    print(f"Connected: {address}")

    with connection:
        with connection.makefile("rb") as reader:
            while True:
                data = reader.readline()

                if not data:
                    break

                message = data.decode().strip()

                print(f"Received from {address}: {message}")

                connection.sendall(b"ACK\n")

    print(f"Disconnected: {address}")


#selve serveren
def start_server():
    server = ThreadingHTTPServer((HOST, PORT), RequestHandler)

    print(f"HTTP Server listening on port {PORT}")

    server.serve_forever()



if __name__ == "__main__":
    start_server()
