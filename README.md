# gethomepage Health Checker

This is meant to be a companion to [gethomepage](https://gethomepage.dev/latest/) and the [Custom Widget API](https://gethomepage.dev/latest/widgets/services/customapi/).

The idea is to allow you to create a custom widget for any arbitrary service. Especially useful for services where a prebuilt widget isn't there. 

Here's an example creating Authentik widget that tells you if the service is online. 

```
- Authentik:
    href: https://authentik.example.com/
    description: Authentik
    widget:
        type: customapi
        url: https://health-check.example.com/
        requestBody:
            host: authentik.example.com
            path: /-/health/live/
            method: get
        headers:
            content-type: application/json
        method: POST
        refreshInterval: 60000 # optional - in milliseconds, defaults to 10s, set to 1min here
        mappings:
            - field: success
            label: Up
            format: text
```

Using [httpie](https://httpie.io/) the request looks like this

```
❯ http https://authentik.example.com/
HTTP/1.1 204 No Content
CF-Cache-Status: DYNAMIC
CF-RAY: 885e87c438799b76-FRA
Connection: keep-alive
Content-Encoding: gzip
Content-Type: text/html; charset=utf-8
Date: Sat, 18 May 2024 20:17:22 GMT
NEL: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}
Server: cloudflare
alt-svc: h3=":443"; ma=86400
referrer-policy: same-origin
vary: Accept-Encoding, Cookie
x-authentik-id: 3f5a3a8e46c64d48ada5ea0b69ad1e3f
x-content-type-options: nosniff
x-frame-options: DENY
x-powered-by: authentik
```

For another example, here's a custom widget for a docker registry.

```
- Docker Registry:
    href: https://registry.example.com/
    description: My self hosted docker container repo
    widget:
        type: customapi
        url: https://health-check.example.com/
        requestBody:
            host: registry.example.com
            path: /v2/
            method: get
        headers:
            content-type: application/json
        method: POST
        refreshInterval: 60000 # optional - in milliseconds, defaults to 10s. Set to 1min
        mappings:
            - field: success
            label: Up
            format: text
```

That same example run from [httpie](https://httpie.io/).

```
❯ http https://registry.example.com/v2/
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 2
Content-Type: application/json; charset=utf-8
Date: Sat, 18 May 2024 20:29:19 GMT
Docker-Distribution-Api-Version: registry/2.0
Server: nginx/1.18.0 (Ubuntu)
X-Content-Type-Options: nosniff

{}
```

There's a lot more you can do with mappings. 

Lastly, here's an example of a resource protected by [Cloudflare Access service token](https://developers.cloudflare.com/cloudflare-one/identity/service-tokens/).

```
- CF Access App:
        href: https://app.example.com/
        description: My extremely cool web app
        widget:
            type: customapi
            url: https://health-check.example.com/
            method: POST
            headers:
                content-type: application/json
            requestBody:
              host: app.example.com
              path: /health-check
              method: get
              cloudflareAccess: true
            refreshInterval: 60000 # optional - in milliseconds, defaults to 10s. Set to 2hr
```
