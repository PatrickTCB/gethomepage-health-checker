#!/bin/sh
docker run -d --restart always --name gethomepage-health-check -p 127.0.0.1:9026:8080 gethomepagehealthcheck