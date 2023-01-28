# Simple dynamic ip updater for nginx proxy manager
Updates proxy forward ip using with public ip
- Use **config.js** to setup the script:
    - base_url - nginx proxy manager base domain/ip including schema
    - email - nginx proxy manager user email
    - password - nginx proxy manager user password
    - recheck_mins - simple timeout between ip is rechecked for changes
    - proxy_replace - list of proxy ids, proxy id can be seen when clicking on proxy edit as **Proxy Host #id**
