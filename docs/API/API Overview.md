<style>
div.wy-nav-content {
    max-width: 1100px;
}
</style>
##### Curl Example

For local PostMaster authentication, use the following command (session.txt is used to store your login session):  
```bash
curl https://postmaster.example.local/login --data 'username=admin&password=PostMaster&auth_source=PostMaster User' -c session.txt
```

For LDAP authentication, set auth_source with the value from the "AD Domain" setting on the configurations page (session.txt is used to store your login session):
```bash
curl https://postmaster.example.local/login --data 'username=user@example.local&password=password&auth_source=example.local' -c session.txt
```

Once you are logged in, you can use the following command to query the API:
```bash
curl https://postmaster.example.local/api/v1/domains -b session.txt
```

##### PowerShell Example (v3+)
For local PostMaster authentication, use the following command (session is a variable used to store your login session):  
```powershell
Invoke-WebRequest -Uri 'http://postmaster.example.local/login' -Method 'Post' -SessionVariable 'session' -Body @{username = 'admin'; password = 'PostMaster'; auth_source = 'PostMaster User'}
```

For LDAP authentication, set auth_source with the value from the "AD Domain" setting on the configurations page (session is a variable used to store your login session):
```powershell
Invoke-WebRequest -Uri 'http://postmaster.example.local/login' -Method 'Post' -SessionVariable 'session' -Body @{username = 'admin'; password = 'password'; auth_source = 'example.local'}
```

Once you are logged in, you can use the following command to query the API:
```powershell
Invoke-RestMethod -Uri 'http://postmaster.example.local/api/v1/domains' -WebSession $session
```

### API Documentation

**API Spec:** [OpenAPI (Swagger)](/Api/openAPI-spec.html)  
**API Spec File:** [OpenAPI (Swagger)](/Api/openAPI-spec.yml)
