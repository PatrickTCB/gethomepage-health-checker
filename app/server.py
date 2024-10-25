# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
import json
import os
import curlify
from lib import web

class APIEndPoint:
    def toDict(self):
        dv = {}
        dv["method"] = self.method
        dv["getParams"] = self.getParams
        dv["postParams"] = self.postParams
        dv["server"] = self.server
        dv["path"] = self.path
        dv["body"] = self.body
        dv["headers"] = self.headers
        return dv
    method = ""
    getParams = {}
    postParams = {}
    headers = {}
    path = ""
    server = ""
    body = ""
    
def getParamsFromPath(path) :
    getParamsDict = {}
    if "?" in path:
        pathSplit = path.split("?", 1)
        print(str(pathSplit))
        if "&" in pathSplit[1]:
            paramsRaw = pathSplit[1].split("&")
            for pRaw in paramsRaw:
                pSplit = pRaw.split("=")
                if len(pSplit) == 2:
                    getParamsDict[str(pSplit[0])] = str(pSplit[1])
        elif "=" in pathSplit[1]:
            pSplit = pathSplit[1].split("=")
            if len(pSplit) == 2:
                getParamsDict[str(pSplit[0])] = str(pSplit[1])
    return getParamsDict

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
        if "origin" not in endpoint.headers.keys():
            endpoint.headers["origin"] = ""
        print("Trying to build " + endpoint.path + " as an json response page. After " + endpoint.method + " request.")
        endpoint.getParams = getParamsFromPath(self.path)
        if endpoint.method == "POST":
            content_length = endpoint.headers['Content-Length']
            length = int(content_length) if content_length else 0
            ctype, pdict = parse_header(self.headers['content-type'])
            postvars = ""
            if ctype == 'multipart/form-data':
                postvars = parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['Content-Length'])
                postvars = parse_qs(
                        self.rfile.read(length), keep_blank_values=1)
            elif ctype == 'application/json':
                endpoint.postParams = json.loads(self.rfile.read(length))
            else:
                try: 
                    content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
                    post_data = self.rfile.read(content_length) # <--- Gets the data itself
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
        # we turn it into json and that's our response body. 
        responseDict = {}
        # A bunch of dictionary build ing junk happens here
        responseDict["success"] = False
        if ("method" in endpoint.postParams.keys()) and ("host" in endpoint.postParams.keys()) and ("path" in endpoint.postParams.keys()):
            if endpoint.postParams["method"] == "get":
                cloudflareAccess = False
                if "cloudflareAccess" in endpoint.postParams.keys():
                    cloudflareAccess = True
                r = web.get(endpoint.postParams["host"], endpoint.postParams["path"], cloudflareAccess=cloudflareAccess, printMe=False)
                if r == False:
                    self.send_response(403)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    responseDict["host"] = endpoint.postParams["host"]
                    responseDict["path"] = endpoint.postParams["path"]
                    responseDict["cloudflareAccess"] = cloudflareAccess
                    print("{}".format(json.dumps(responseDict)))
                else:
                    if int(r.status_code) in [200, 201, 202]:
                        self.send_response(200)
                        responseDict["success"] = True
                    else:
                        self.send_response(int(r.status_code))
                        responseDict["success"] = False
                        print("Failed request: {}".format(curlify.to_curl(r.request)))
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    responseDict["host"] = endpoint.postParams["host"]
                    responseDict["path"] = endpoint.postParams["path"]
                    responseDict["cloudflareAccess"] = cloudflareAccess
                    responseDict["status"] = int(r.status_code)
                    try:
                        jsonOutput = json.loads(r.text)
                        print("Response: {}".format(json.dumps(jsonOutput)))
                    except:
                        print("Response skipped as it wasn't JSON")
                    print("{}".format(json.dumps(responseDict)))
            elif endpoint.postParams["method"] == "options":
                cloudflareAccess = False
                if "cloudflareAccess" in endpoint.postParams.keys():
                    cloudflareAccess = True
                r = web.options(endpoint.postParams["host"], endpoint.postParams["path"], cloudflareAccess=cloudflareAccess, printMe=False)
                if int(r.status_code) in [200, 201, 202]:
                    self.send_response(200)
                    responseDict["success"] = True
                else:
                    self.send_response(int(r.status_code))
                    responseDict["success"] = False
                    print("Failed request: {}".format(curlify.to_curl(r.request)))
                self.send_header("Content-type", "application/json")
                self.end_headers()
                responseDict["host"] = endpoint.postParams["host"]
                responseDict["path"] = endpoint.postParams["path"]
                responseDict["cloudflareAccess"] = cloudflareAccess
                responseDict["status"] = int(r.status_code)
                try:
                    jsonOutput = json.loads(r.text)
                    print("Response: {}".format(json.dumps(jsonOutput)))
                except:
                    print("Response skipped as it wasn't JSON")
                print("{}".format(json.dumps(responseDict)))
            elif endpoint.postParams["method"] == "head":
                cloudflareAccess = False
                if "cloudflareAccess" in endpoint.postParams.keys():
                    cloudflareAccess = True
                r = web.head(endpoint.postParams["host"], endpoint.postParams["path"], cloudflareAccess=cloudflareAccess, printMe=False)
                if int(r.status_code) in [200, 201, 202]:
                    self.send_response(200)
                    responseDict["success"] = True
                else:
                    self.send_response(int(r.status_code))
                    responseDict["success"] = False
                    print("Failed request: {}".format(curlify.to_curl(r.request)))
                self.send_header("Content-type", "application/json")
                self.end_headers()
                responseDict["host"] = endpoint.postParams["host"]
                responseDict["path"] = endpoint.postParams["path"]
                responseDict["cloudflareAccess"] = cloudflareAccess
                responseDict["status"] = int(r.status_code)
                try:
                    jsonOutput = json.loads(r.text)
                    print("Response: {}".format(json.dumps(jsonOutput)))
                except:
                    print("Response skipped as it wasn't JSON")
                print("{}".format(json.dumps(responseDict)))
            print("----")
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
