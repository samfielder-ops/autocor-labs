import os
from pprint import pprint
from scrapli.driver.core import IOSXEDriver
from scrapli.exceptions import (
    ScrapliAuthenticationFailed,
    ScrapliTimeout,
    ScrapliConnectionError,
    ScrapliException
)

#variables
username = os.environ.get('USER')
password = os.environ.get('PASS')
switches = ["172.16.100.21", "172.16.100.22"]
vlans = [{"id": 10, "name": "DATA"}, {"id": 20, "name": "VOICE"}, {"id": 30, "name": "MGMT"}]

def connect(s):
        device = {
            "transport": "system",
            "host": s,
            "auth_username": username,
            "auth_password": password,
            "auth_strict_key": False
        }
        try:
            con = IOSXEDriver(**device)
            #REMEVER THIS
            con.open()
            #print(con)

            print(f"Connected to {s}")
            return con
        except ScrapliAuthenticationFailed:
            print(f"Authentication Failure on {s}")
        except ScrapliTimeout:
            print(f"Timeout on {s}")
        except ScrapliConnectionError:
            print(f"Connection Failure on {s}")
        except ScrapliException as e:
            print(f"Scrapli General Exception on {s} : {e}")

def configure_vlans(con):
    cmds = []
    for v in vlans:
        cmds += [f"vlan {v['id']}", f" name {v['name']}"]
    #print(cmds)
    con.send_configs(cmds)
    #print(config)

def verify_vlans(con):
    result = con.send_command("show vlan brief")
    matched_vlans = []
    for v in result.textfsm_parse_output():
        if v["vlan_id"] in ["10","20","30"]:
            print(f"VLAN {v['vlan_id']} Found")
            matched_vlans.append({
                "id": v["vlan_id"], 
                "name": v["vlan_name"], 
                "status": v["status"]
            })
    return matched_vlans

def main():
    for s in switches:
        con = connect(s)
        configure_vlans(con)
        con.send_command("write memory")
        result = verify_vlans(con)
        pprint(result)
        con.close()

if __name__ == "__main__":
    main()