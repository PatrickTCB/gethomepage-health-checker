import requests
import json
from urllib.parse import urljoin

def saveResponse(fileName, contentsRaw):
    contents = str(contentsRaw)
    with open(fileName, "w+") as output_file:
        output_file.write(contents)
        output_file.close()

def get(host, path, printMe=False, ignoreErrors=False, session=None):
    fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    if session == None:
        s = requests.Session()
    else:
        s = session
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
        print("Attempted to get " + str(path))
        responseName = "error-{}{}.json".format(result.status_code, path.replace("/", "."))
        try:
            responseDict = json.loads(result.text)
            responseDict["path called"] = path
            saveResponse(responseName, json.dumps(responseDict))
        except:
            saveResponse(responseName, result.text)
        print("Error response saved to {}".format(responseName))
        return False

def options(host, path, printMe=False, session=None):
    fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    if session == None:
        s = requests.Session()
    else:
        s = session
    result = s.options(fullurl)
    if printMe:
        print("Result: {}".format(result.status_code))
    return result
    
def head(host, path, printMe=False, session=None):
    fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    if session == None:
        s = requests.Session()
    else:
        s = session
    result = s.head(fullurl)
    if printMe:
        print("Result: {}".format(result.status_code))
    return result

def post(host, path, contentType, body={}, printMe=False, session=None):
    fullurl = urljoin("https://{}".format(host), path)
    if printMe:
        print("Trying: {}".format(fullurl))
    if session == None:
        s = requests.Session()
    else:
        s = session
    s.headers["Content-Type"] = contentType
    
    result = s.post(fullurl, data=body)
    if printMe:
        print(str(result.text))
    if result.status_code > 199 and result.status_code < 300:
        return result
    else:
        print("Error when retrieving info from Akamai")
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
