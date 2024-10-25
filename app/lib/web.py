import requests
import json
import os
from urllib.parse import urljoin

def saveResponse(fileName, contentsRaw):
    contents = str(contentsRaw)
    with open(fileName, "w+") as output_file:
        output_file.write(contents)
        output_file.close()

def get(host, path, headers={}, cloudflareAccess=False, printMe=False, ignoreErrors=False, session=None):
    if "https://" in host or "http://" in host:
        fullurl = urljoin(host, path)
    else:
        fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    if session == None:
        s = requests.Session()
    else:
        s = session
    for k in headers.keys():
        s.headers[k] = headers[k]
    if cloudflareAccess:
        s.headers["CF-Access-Client-Id"] = os.environ["CFClientID"]
        s.headers["CF-Access-Client-Secret"] = os.environ["CFClientSecret"]
    result = s.get(fullurl)
    if printMe:
        print(str(result.text))
    if result.status_code > 199 and result.status_code < 300:
        return result
    else:
        if ignoreErrors:
            return False
        print("Error when retrieving info from {}".format(host))
        print("Status: " + str(result.status_code))
        print("Attempted to get {}".format(fullurl))
        responseName = "error-{}{}.json".format(result.status_code, str(fullurl.replace("https:", "")).replace("/", "."))
        try:
            responseDict = json.loads(result.text)
            responseDict["path called"] = path
            saveResponse(responseName, json.dumps(responseDict))
        except:
            saveResponse(responseName, result.text)
        print("Error response saved to {}".format(responseName))
        return False

def options(host, path, headers={}, cloudflareAccess=False, printMe=False, session=None):
    if "https://" in host or "http://" in host:
        fullurl = urljoin(host, path)
    else:
        fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    if session == None:
        s = requests.Session()
    else:
        s = session
    for k in headers.keys():
        s.headers[k] = headers[k]
    if cloudflareAccess:
        s.headers["CF-Access-Client-Id"] = os.environ["CFClientID"]
        s.headers["CF-Access-Client-Secret"] = os.environ["CFClientSecret"]
    result = s.options(fullurl)
    if printMe:
        print("Result: {}".format(result.status_code))
    return result
    
def head(host, path, headers={}, cloudflareAccess=False, printMe=False, session=None):
    if "https://" in host or "http://" in host:
        fullurl = urljoin(host, path)
    else:
        fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    if session == None:
        s = requests.Session()
    else:
        s = session
    for k in headers.keys():
        s.headers[k] = headers[k]
    if cloudflareAccess:
        s.headers["CF-Access-Client-Id"] = os.environ["CFClientID"]
        s.headers["CF-Access-Client-Secret"] = os.environ["CFClientSecret"]
    result = s.head(fullurl)
    if printMe:
        print("Result: {}".format(result.status_code))
    return result

def post(host, path, contentType, body={}, headers={}, cloudflareAccess=False, printMe=False, session=None):
    if "https://" in host or "http://" in host:
        fullurl = urljoin(host, path)
    else:
        fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    if session == None:
        s = requests.Session()
    else:
        s = session
    s.headers["Content-Type"] = contentType
    for k in headers.keys():
        s.headers[k] = headers[k]
    if cloudflareAccess:
        s.headers["CF-Access-Client-Id"] = os.environ["CFClientID"]
        s.headers["CF-Access-Client-Secret"] = os.environ["CFClientSecret"]
    
    result = s.post(fullurl, data=body)
    if printMe:
        print(str(result.text))
    if result.status_code > 199 and result.status_code < 300:
        return result
    else:
        print("Error when retrieving info from {}".format(host))
        print("Status: " + str(result.status_code))
        print("Attempted to get " + str(path))
        responseName = "error-{}{}.json".format(result.status_code, host, path.replace("/", "."))
        try:
            responseDict = json.loads(result.text)
            responseDict["host"] = host
            responseDict["path called"] = path
            responseDict["requestBody"] = body
            saveResponse(responseName, json.dumps(responseDict))
        except:
            saveResponse(responseName, result.text)
        print("Error response saved to {}".format(responseName))
        return False
