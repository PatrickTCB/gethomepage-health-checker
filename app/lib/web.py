import requests
import json
import os
from urllib.parse import urljoin

def saveResponse(fileName, contentsRaw):
    contents = str(contentsRaw)
    with open(fileName, "w+") as output_file:
        output_file.write(contents)
        output_file.close()

def get(host, path, headers={}, printMe=False, conf={}):
    if "https://" in host or "http://" in host:
        fullurl = urljoin(host, path)
    else:
        fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    s = requests.Session()
    for k in headers.keys():
        s.headers[k] = headers[k]
    if "custom_headers" in conf.keys():
        customHeaderDomains = conf["custom_header_domains"]
        if host in customHeaderDomains:
            customHeaders = conf["custom_headers"]
            for h in customHeaders.keys():
                s.headers[h] = customHeaders[h]
    result = s.get(fullurl)
    if printMe:
        print(str(result.text))
    if result.status_code > 199 and result.status_code < 300:
        return result
    else:
        print("Error when retrieving info from {}".format(host))
        print("Status: " + str(result.status_code))
        print("Attempted to get {}".format(fullurl))
        responseName = "error-{}{}.json".format(result.status_code, str(fullurl.replace("https:", "")).replace("/", "."))
        try:
            responseDict = json.loads(result.text)
            responseDict["path"] = path
            responseDict["responseHeaders"] = dict(result.headers)
            try:
                import curlify
                requestSent = result.request
                responseDict["curl"] = curlify.to_curl(requestSent)
            except:
                print("Couldn't add curl version of request to error dict\nInstall curlify if you want that to work.")
            saveResponse(responseName, json.dumps(responseDict, default=str))
        except:
            output = {}
            output["headers"] = dict(result.headers)
            output["text"] = result.text
            try:
                import curlify
                requestSent = result.request
                output["curl"] = curlify.to_curl(requestSent)
            except:
                print("Couldn't add curl version of request to error dict\nInstall curlify if you want that to work.")
            saveResponse(responseName, json.dumps(output, default=str))
        print("Error response saved to {}".format(responseName))
        return result

def options(host, path, headers={}, printMe=False, conf={}):
    if "https://" in host or "http://" in host:
        fullurl = urljoin(host, path)
    else:
        fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    s = requests.Session()
    for k in headers.keys():
        s.headers[k] = headers[k]
    if "custom_headers" in conf.keys():
        customHeaderDomains = conf["custom_header_domains"]
        if host in customHeaderDomains:
            customHeaders = conf["custom_headers"]
            for h in customHeaders.keys():
                s.headers[h] = customHeaders[h]
    result = s.options(fullurl)
    if printMe:
        print("Result: {}".format(result.status_code))
    return result
    
def head(host, path, headers={}, printMe=False, conf={}):
    if "https://" in host or "http://" in host:
        fullurl = urljoin(host, path)
    else:
        fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    s = requests.Session()
    for k in headers.keys():
        s.headers[k] = headers[k]
    if "custom_headers" in conf.keys():
        customHeaderDomains = conf["custom_header_domains"]
        if host in customHeaderDomains:
            customHeaders = conf["custom_headers"]
            for h in customHeaders.keys():
                s.headers[h] = customHeaders[h]
    result = s.head(fullurl)
    if printMe:
        print("Result: {}".format(result.status_code))
    return result

def post(host, path, contentType, body={}, headers={}, printMe=False, conf={}):
    if "https://" in host or "http://" in host:
        fullurl = urljoin(host, path)
    else:
        fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    s = requests.Session()
    s.headers["Content-Type"] = contentType
    for k in headers.keys():
        s.headers[k] = headers[k]
    if "custom_headers" in conf.keys():
        customHeaderDomains = conf["custom_header_domains"]
        if host in customHeaderDomains:
            customHeaders = conf["custom_headers"]
            for h in customHeaders.keys():
                s.headers[h] = customHeaders[h]
    result = s.post(fullurl, data=body)
    if printMe:
        print(str(result.text))
    if result.status_code > 199 and result.status_code < 300:
        return result
    else:
        print("Error when retrieving info from {}".format(host))
        print("Status: " + str(result.status_code))
        print("Attempted to get " + str(path))
        responseName = "error-{}{}.json".format(result.status_code, host.replace("https://", ""), path.replace("/", "."))
        try:
            responseDict = json.loads(result.text)
            responseDict["path"] = path
            responseDict["responseHeaders"] = dict(result.headers)
            try:
                import curlify
                requestSent = result.request
                responseDict["curl"] = curlify.to_curl(requestSent)
            except:
                print("Couldn't add curl version of request to error dict\nInstall curlify if you want that to work.")
            saveResponse(responseName, json.dumps(responseDict, default=str))
        except:
            output = {}
            output["headers"] = dict(result.headers)
            output["text"] = result.text
            try:
                import curlify
                requestSent = result.request
                output["curl"] = curlify.to_curl(requestSent)
            except:
                print("Couldn't add curl version of request to error dict\nInstall curlify if you want that to work.")
            saveResponse(responseName, json.dumps(output, default=str))
        print("Error response saved to {}".format(responseName))
        return result
