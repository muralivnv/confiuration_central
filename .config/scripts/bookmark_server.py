#!/usr/bin/python3

import http.server
import socketserver
import os
from mistletoe import Document, HTMLRenderer
from argparse import ArgumentParser

BOOKMARK_MD_FILE = ""

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # Sending an '200 OK' response
        self.send_response(200)

        # Setting the header
        self.send_header("Content-type", "text/html")

        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()

        contents = ""
        with open(BOOKMARK_MD_FILE) as in_file:
            with HTMLRenderer() as renderer:
                contents = renderer.render(Document(in_file))

        # Writing the HTML contents with UTF-8
        self.wfile.write(bytes(contents, "utf8"))
        return

if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument("-f", "--file", dest="bookmark_file", help="bookmark file",
                      required=True)
    args.add_argument("-p", "--port", dest="PORT", help="port",
                      required=False, default=8000)
    
    parsed_args = args.parse_args()
    BOOKMARK_MD_FILE = parsed_args.bookmark_file
    if not os.path.exists(BOOKMARK_MD_FILE):
        print("[ERROR] specified file does not exist")
        exit(1)

    # Create an object of the above class
    bookmark_server = socketserver.TCPServer(("localhost", parsed_args.PORT),
                                             MyHttpRequestHandler,
                                             bind_and_activate=False)
    bookmark_server.allow_reuse_address = True
    bookmark_server.server_bind()
    bookmark_server.server_activate()

    # Start the server
    try:
        print(f"running server at -- http://localhost:{parsed_args.PORT}")
        bookmark_server.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        bookmark_server.server_close()