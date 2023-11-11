import os
import time
import copy
import requests
from dotenv import load_dotenv

load_dotenv()

# https://cfapi.centminmod.com/#cloudflare-tunnel-configuration-put-configuration works on Cloudflare API v4
# The code runs on the assumptio that all service under the tunnel IP's are the same

# Edit the env file:
cf_api_token = os.getenv('cf_api_token') 
cf_account_id = os.getenv('cf_account_id')
cf_tunnel_id = os.getenv('cf_tunnel_id')
cf_zone_id = os.getenv('cf_zone_id')
cf_dns_name = os.getenv('cf_dns_name')

time_cycle = 300 # Wait period before checking if IP has changed in seconds: 300s -> 5min
connection_time_out_interval = 30 # If ip_api fails try again in 30 seconds
ip_api = "https://api.ipify.org" # The server which responds with your ipv4 address

def get_tunnel_config(cf_api_token, cf_account_id, cf_tunnel_id):
    url = f'https://api.cloudflare.com/client/v4/accounts/{cf_account_id}/cfd_tunnel/{cf_tunnel_id}/configurations'
    headers = {"Authorization": f"Bearer {cf_api_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def put_tunnel_config(cf_api_token, cf_account_id, cf_tunnel_id, updated_config):
    url = f'https://api.cloudflare.com/client/v4/accounts/{cf_account_id}/cfd_tunnel/{cf_tunnel_id}/configurations'
    headers = {'Authorization': f'Bearer {cf_api_token}', 'Content-Type': 'application/json'}

    payload = {'config': updated_config}
    response = requests.put(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("Configuration updated successfully.") 
    else:
        print(f"Error {response.status_code}: {response.text}")

def write_to_file(string, filename="host_ip.txt"):
    try:
        with open(filename, "w") as file:
            file.write(str(string))
        print(f"Logs written to {filename}")
    except Exception as e:
        print(f"Error writing to file: {e}")

def change_json_data_ip(json_dict, ip):
    for public_domain in json_dict["config"]["ingress"]:
        if public_domain["service"] == "http_status:404":
            continue
        protocol = f"{public_domain['service'].split('://')[0]}://"
        port = f":{public_domain['service'].split(':')[-1]}"
        public_domain_ip = str(protocol + ip + port)
        public_domain["service"] = public_domain_ip
        print(public_domain_ip)
    return json_dict

def get_ip_from_config_json(conf_json):
    ip = None
    for public_domain in conf_json["config"]["ingress"]:
        if public_domain["service"] == "http_status:404":
            continue
        ip = str(public_domain["service"]).split("://")[1].split(":")[0]
        print(ip)
        if ip is not None:
            return ip
    return ip

def change_data(data, host_ip):
    new_data = copy.deepcopy(data["result"])
    new_data = change_json_data_ip(new_data, host_ip)
    put_tunnel_config(cf_api_token,cf_account_id,cf_tunnel_id, new_data["config"])
    write_to_file({'config': new_data},"current_conf")

def get_host_ip():
    try:
        response = requests.get(ip_api)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error: Unable to fetch IP address. Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting host IP address: {e}")
        write_to_file(str(e), "failedlog.txt")
        return None

def main():
    working = True
    host_ip = get_host_ip() 
    if host_ip == None:
        working = False
        print("Fail: Could not resolve host IP")
    cloudflare_conf_ip = get_tunnel_config(cf_api_token,cf_account_id,cf_tunnel_id)
    curr_cf_ip = get_ip_from_config_json(cloudflare_conf_ip["result"])
    prev_ip = host_ip
    if host_ip != curr_cf_ip: # To save on api requests to cloudflare - only check once then only check changes from the previous
        print(f"host_ip: {host_ip} and cloudflare service IP: {curr_cf_ip} dont match")
        change_data(cloudflare_conf_ip, host_ip)
    print(f"host_ip: {host_ip} and cloudflare service IP: {curr_cf_ip} match. Setting previous IP and checking again in {time_cycle}s")
    while working:
        host_ip = get_host_ip()
        print(f"curr host IP: {host_ip}")
        if host_ip:       
            if host_ip != prev_ip: # IP has changed!
                print(f"curr host IP: {host_ip} did not match previous IP, changing Cloudfalre tunnel config...")
                prev_ip = host_ip
                result = get_tunnel_config(cf_api_token,cf_account_id,cf_tunnel_id)
                change_data(result, host_ip)
        else:
            print(f"Fail: Could not resolve host IP: most like no internet access trying again in {connection_time_out_interval}s")
            time.sleep(connection_time_out_interval)
            continue
        print(f"IP has not changed checking again in {time_cycle}s")
        time.sleep(time_cycle) #300s 5min
 

if __name__ == "__main__":
    main()




