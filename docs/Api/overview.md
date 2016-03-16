# The Postmaster API


Basic usage:  
```
curl 'http://postmaster.example/login' --data 'username=user@postmaster.com&password=password&auth_source=PostMaster User'
```
Get the session cookie from the response. This is your authentication token.

```
curl --cookie "session=[long session id]" https://postmaster.example/api/v1/domains
```

API Spec: [OpenAPI (Swagger)](/Api/openAPI-spec.html)  
API Spec File: [OpenAPI (Swagger)](/Api/openAPI-spec.yml)
