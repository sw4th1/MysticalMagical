# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import os

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
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


        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
    
if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")