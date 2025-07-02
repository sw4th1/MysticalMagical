# Python 3 server example
from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl
import time
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.process_user_data import reformat_spotify_data
from scripts.make_haystack_docs import convert_to_haystack_docs
from src.run_query import run_query_loop
from scripts.add_to_queue import add_tracks_to_queue

hostName = "localhost"
serverPort = 8080

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

class MyServer(SimpleHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print(post_data)
        my_json = post_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)
        print(data)

        type = data.get("type")
        if (type == "data"):
            new_data = data['payload']
            with open(os.path.join(os.getcwd(), 'llm-music\\data\\raw_data.json'), 'r+') as file:
                old_data = json.load(file)
                old_data.append(new_data)
                file.seek(0)
                file.truncate(0)
                json.dump(old_data, file, indent=4)
            reformat_spotify_data()
            convert_to_haystack_docs()
        elif (type == "remove"):
            user_id = data['payload']
            with open(os.path.join(os.getcwd(), 'llm-music\\data\\raw_data.json'), 'r+') as file:
                old_data = json.load(file)
                new_data = []
                for i in old_data:
                    if (i["user_id"] != user_id):
                        new_data.append(i)
                file.seek(0)
                file.truncate(0)
                json.dump(new_data, file, indent=4)
                # add code for sending recently played here
        elif (type == "settings"):
            payload = data['payload']
            prompt = payload['filter']
            results = run_query_loop(prompt)
            add_tracks_to_queue(results)
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(MyServer, self).end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()    

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    webServer.socket = context.wrap_socket(webServer.socket, server_side=True)

    # webServer.socket = ssl.wrap_socket(
    #     webServer.socket,
    #     keyfile="path/to/your/private.key",  # Path to your private key
    #     certfile="path/to/your/certificate.crt",  # Path to your certificate
    #     server_side=True
    # )

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")