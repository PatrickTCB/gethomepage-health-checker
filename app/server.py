# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
import json
import os
from lib import web

class APIEndPoint:
    def toDict(self):
        dv = {}
        dv["method"] = self.method
        dv["postParams"] = self.postParams
        dv["server"] = self.server
        dv["path"] = self.path
        dv["body"] = self.body
        dv["headers"] = self.headers
        return dv
    method = ""
    postParams = {}
    headers = {}
    path = ""
    server = ""
    body = ""

serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_POST(self):
        endpoint = APIEndPoint()
        endpoint.method = "POST"
        endpoint.path = self.path.split("?")[0]
        endpoint.server = os.environ["FQDN"]
        endpoint.postParams = {}
        endpoint.body = ""
        endpoint.headers = {}
        #print("Recieved request with headers: {}".format(self.headers))
        for header in self.headers.items():
            try:
                endpoint.headers[header[0]] = header[1]
            except:
                print("Couldn't understand header: {}".format(header))
        print("Headers: {}".format(json.dumps(endpoint.headers)))
        if "origin" not in endpoint.headers.keys():
            endpoint.headers["origin"] = ""
        print("Trying to build " + endpoint.path + " as an json response page. After " + endpoint.method + " request.")
        if endpoint.method == "POST":
            content_length = endpoint.headers['Content-Length']
            length = int(content_length) if content_length else 0
            ctype, pdict = parse_header(self.headers['content-type'])
            postvars = ""
            if ctype == 'multipart/form-data':
                postvars = parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                postvars = parse_qs(self.rfile.read(length), keep_blank_values=1)
            elif ctype == 'application/json':
                endpoint.postParams = json.loads(self.rfile.read(length))
            else:
                try: 
                    post_data = self.rfile.read(length)
                    endpoint.body = post_data.decode("utf-8")
                except Exception as e:
                    print("Couldn't parse POST body")
                    print(e)
                postvars = {}
            if len(postvars) > 0:
                for key in postvars.keys():
                    pvlist = postvars[key]
                    if len(pvlist) == 1:
                        endpoint.postParams[key.decode("utf-8")] = postvars[key][0].decode("utf-8")
                    else:
                        pvstringlist = []
                        for pv in postvars[key]:
                            pvstringlist.append(pv.decode("utf-8"))
                        endpoint.postParams[key.decode("utf-8")] = pvstringlist
        responseDict = {}
        responseDict["success"] = False
        if ("method" in endpoint.postParams.keys()) and ("host" in endpoint.postParams.keys()) and ("path" in endpoint.postParams.keys()):
            if endpoint.postParams["method"] == "get":
                r = web.get(endpoint.postParams["host"], endpoint.postParams["path"], True)
                if r == False:
                    self.send_response(403)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    responseDict["host"] = endpoint.postParams["host"]
                    responseDict["path"] = endpoint.postParams["path"]
                    print("{}".format(json.dumps(responseDict)))
                else:
                    if int(r.status_code) > 199 and int(r.status_code) < 300:
                        # see README for info on status codes
                        self.send_response(200)
                        responseDict["success"] = True
                    else:
                        self.send_response(int(r.status_code))
                        responseDict["success"] = False
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    responseDict["host"] = endpoint.postParams["host"]
                    responseDict["path"] = endpoint.postParams["path"]
                    responseDict["status"] = int(r.status_code)
                    print("Response: {}".format(r.text))
                    print("{}".format(json.dumps(responseDict)))
            elif endpoint.postParams["method"] == "options":
                r = web.options(endpoint.postParams["host"], endpoint.postParams["path"])
                if int(r.status_code) > 199 and int(r.status_code) < 300:
                    self.send_response(200)
                    responseDict["success"] = True
                else:
                    self.send_response(int(r.status_code))
                    responseDict["success"] = False
                self.send_header("Content-type", "application/json")
                self.end_headers()
                responseDict["success"] = True
                responseDict["host"] = endpoint.postParams["host"]
                responseDict["path"] = endpoint.postParams["path"]
                responseDict["status"] = int(r.status_code)
                print("Response: {}".format(r.text))
                print("{}".format(json.dumps(responseDict)))
            elif endpoint.postParams["method"] == "head":
                r = web.head(endpoint.postParams["host"], endpoint.postParams["path"])
                if int(r.status_code) > 199 and int(r.status_code) < 300:
                    self.send_response(200)
                    responseDict["success"] = True
                else:
                    self.send_response(int(r.status_code))
                    responseDict["success"] = False
                self.send_header("Content-type", "application/json")
                self.end_headers()
                responseDict["success"] = True
                responseDict["host"] = endpoint.postParams["host"]
                responseDict["path"] = endpoint.postParams["path"]
                responseDict["status"] = int(r.status_code)
                print("Response: {}".format(r.text))
                print("{}".format(json.dumps(responseDict)))
        else:
            self.send_response(501)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            print("This request coludn't be understood\n{}".format(json.dumps(endpoint.toDict())))
            # Time to build the json response. Our basic plan here is to build a nice little dictionary, then in the last step
        # Now that our response dictionary has been built, we can give it back to the requester.
        self.wfile.write(bytes(json.dumps(responseDict), "utf-8"))
        #Done :)

if __name__ == "__main__":        
    webServer = HTTPServer(("", serverPort), MyServer)
    print("Server started http://localhost:%s" % (serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
