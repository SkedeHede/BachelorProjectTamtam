#https://docs.python.org/3/library/http.server.html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import time
#http.server er beregnet til brug af udvikling og test, ikke produktion (grundet sikkerhed)
HOST = "0.0.0.0"
PORT = 5000
PROCESSING_DELAY = 0.01  # 10 ms
data = b"A" * 10240 #Data, der sendes som svar til klienten (10*1024 = 10240 bytes ≈ 10 KB)

class RequestHandler(BaseHTTPRequestHandler):
    #BaseHTTPRequestHandler bruger HTTP/1.0 som standard.
    protocol_version = "HTTP/1.1" #ændres til HTTP/1.1 for at understøtte persistent connections (altså pipelining)
    def do_GET(self): #Håndterer HTTP GET-requests
        time.sleep(PROCESSING_DELAY) #vent 10 ms for at simulere serverbehandlingstid. tcp handshake tager 20ms nu
        self.send_response(200) #Returnerer en 200 OK statuskode, som fortæller at serveren har modtaget og forstået requesten
        self.send_header("Content-type", "text/plain") #Angiver at indholdet af svaret er almindelig tekst
        self.send_header("Content-Length", str(len(data)))
        self.end_headers() #Afslutter HTTP-headeren, så serveren kan begynde at sende selve svaret
        self.wfile.write(data) #Sender data som svar til klienten

    def log_message(self, format, *args):
        return  #Deaktiverer standard logning af HTTP-requests, så serveren ikke logger hver request til konsollen


#selve serveren
def start_server():
    server = ThreadingHTTPServer((HOST, PORT), RequestHandler) #threadingHTTPServer bruger TCP som kommunikation

    print(f"HTTP Server listening on port {PORT}")

    server.serve_forever()



if __name__ == "__main__":
    start_server()
