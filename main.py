import json, requests, time
from dateutil import parser
from datetime import datetime

def update_proxies():
    global config, token, proxies, ip
    for id in config["proxy_replace"]:
        # Get proxy by id
        data = [proxy for proxy in proxies if proxy['id'] == id][0]
        # Update proxy
        update_proxy(id, data)

def update_proxy(id: int, data: dict):
    global config, token, ip
    # Update proxy forwad_host, but keep everything else
    res = requests.put(f"{config['base_url']}/api/nginx/proxy-hosts/{id}", 
        json={
            "domain_names": data['domain_names'],
            "forward_scheme": data['forward_scheme'], 
            "forward_host": ip, 
            "forward_port": data['forward_port'], 
            "access_list_id": data['access_list_id'],
            "certificate_id": data['certificate_id'],
            "meta": data['meta'],
            "advanced_config": data['advanced_config'],
            "locations": data['locations'],
            "block_exploits": data['block_exploits'],
            "caching_enabled": data['caching_enabled'],
            "allow_websocket_upgrade": data['allow_websocket_upgrade'],
            "http2_support": data['http2_support'],
            "hsts_enabled": data['hsts_enabled'],
            "hsts_subdomains": data['hsts_subdomains'],
            "ssl_forced": data['ssl_forced']
        }, headers={ "authorization": f"Bearer {token['value']}"})
    
    # Repeat if not successful
    if (res.status_code != 200):
        time.sleep(10)
        update_proxy(id, data)

def request_proxies() -> dict:
    global config, token
    res = requests.get(f"{config['base_url']}/api/nginx/proxy-hosts?expand=owner,access_list,certificate",headers={
        "authorization": f"Bearer {token['value']}"
    })
    
    if (res.status_code == 200):
        return res.json()
    # Repeat if not successful
    time.sleep(10)
    return request_proxies()

def request_public_ip() -> str:
    res = requests.get("https://api.ipify.org?format=json")
    if (res.status_code == 200):
        return res.json()["ip"]
    # Repeat if not successful
    time.sleep(10)
    return request_public_ip()

def request_token() -> dict:
    global config, token
    if (datetime.now().timestamp() < token["expires"]):
        return token
    res = requests.post(f"{config['base_url']}/api/tokens", data={
        "identity": config['email'],
        "secret": config['password']
    })
    
    if (res.status_code == 200):
        data = res.json()

        token["expires"] = parser.parse(data["expires"]).timestamp()
        token["value"] = data["token"]
        return token
    # Repeat if not successful
    time.sleep(10)
    return request_token()

if __name__ == "__main__":
    global config, token, ip, proxies
    with open("./config.json", "r") as fp:
        config = json.load(fp)
        fp.close()
    token = {
        "value": "",
        "expires": 0
    }
    ip = "0.0.0.0"
    while True:
        try:
            token = request_token()
            public_ip = request_public_ip()
            proxies = request_proxies()
            if public_ip != ip:
                ip = public_ip
                update_proxies()
            time.sleep(config["recheck_mins"]*60)
        except Exception as e:
            time.sleep(60)