import http.server
import socketserver
import os
from mistletoe import Document, HTMLRenderer
from argparse import ArgumentParser

BOOKMARK_MD_FILE = ""
PORT = 8000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Sending an '200 OK' response
        self.send_response(200)

        # Setting the header
        self.send_header("Content-type", "text/html")

        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()

        contents = ""
        with open(f"{BOOKMARK_MD_FILE}") as in_file:
            with HTMLRenderer() as renderer:
                contents = renderer.render(Document(in_file))

        # Writing the HTML contents with UTF-8
        self.wfile.write(bytes(contents, "utf8"))
        return

if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument("-f", "--file", dest="bookmark_file", help="bookmark file")
    
    parsed_args = args.parse_args()
    BOOKMARK_MD_FILE = parsed_args.bookmark_file

    # Create an object of the above class
    handler_object = MyHttpRequestHandler
    my_server = socketserver.TCPServer(("", PORT), handler_object)

    # Start the server
    try:
        print(f"running server at -- http://0.0.0.0:{PORT}")
        my_server.serve_forever()
    except KeyboardInterrupt:
        pass
    my_server.server_close()
