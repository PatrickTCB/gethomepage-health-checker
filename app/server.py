# Python 3 server example
import json
import yaml
import hashlib
from typing import Annotated
from pathlib import Path
from typing import Annotated
from fastapi import FastAPI, Request, Form, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from lib import web

class HealthCheck(BaseModel):
    host: str
    path: str
    method: str
    status: int | None = None

app = FastAPI()

@app.post("/", status_code=200)
async def root(hc: HealthCheck, etag: Annotated[str, Header()] = "", if_none_match: Annotated[str, Header()] = ""):
    conf = yaml.safe_load(Path('conf.yml').read_text())
    successStatusCodes = [200, 201, 202]
    if hc.status != None:
        successStatusCodes.append(hc.status)
    if hc.method == "get":
        r = web.get(host=hc.host, path=hc.path, conf=conf)
    elif hc.method == "options":
        r = web.options(host=hc.host, path=hc.path, conf=conf)
    elif hc.method == "head":
        r = web.head(host=hc.host, path=hc.path, conf=conf)
    else:
        # Early exit because methods like "patch" or "post" aren't currently
        # supported by this script.
        errorMessage = "Specificed method '{}' is not currently supported".format(hc.method)
        requestInfo = {"host": hc.host, "path": hc.path}
        responseDict = {"requestInfo": requestInfo}
        responseDict["status"] = 401
        responseDict["success"] = False
        responseDict["message"] = errorMessage
        newEtag = hashlib.md5(str(json.dumps(responseDict)).encode('utf-8')).hexdigest()
        headers = {"Content-Type": "application/json", "ETag": "{}".format(newEtag)}
        return JSONResponse(content=responseDict, headers=headers, status_code=401)
    if r.status_code not in successStatusCodes:
        requestInfo = {"host": hc.host, "path": hc.path}
        responseDict = {"requestInfo": requestInfo}
        responseDict["status"] = r.status_code
        responseDict["success"] = False
        responseDict["message"] = "Your mistake"
        newEtag = hashlib.md5(str(json.dumps(responseDict)).encode('utf-8')).hexdigest()
        headers = {"Content-Type": "application/json", "ETag": "{}".format(newEtag)}
        return JSONResponse(content=responseDict, headers=headers, status_code=401)
    else:
        requestInfo = {"host": hc.host, "path": hc.path}
        responseDict = {"requestInfo": requestInfo}
        responseDict["success"] = True
        responseDict["status"] = r.status_code
        responseDict["message"] = "🎉"
        newEtag = hashlib.md5(str(json.dumps(responseDict)).encode('utf-8')).hexdigest()
        if etag == newEtag or if_none_match == newEtag:
            headers = {"Content-Type": "application/json", "ETag": "{}".format(newEtag)}
            return JSONResponse(content=b'', headers=headers, status_code=304)
        else:
            headers = {"Content-Type": "application/json", "ETag": "{}".format(newEtag)}
            return JSONResponse(content=responseDict, headers=headers)