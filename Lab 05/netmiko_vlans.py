"""
connect to both switches, push VLANs 10/20/30 from a Python data structure with
send_config_set , save config, and verify by parsing show vlan brief output. Hand
"""

from netmiko import ConnectHandler 
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

import os, getpass, sys
import pprint

# Variables
username = os.environ.get('USER')
password = getpass.getpass("Enter Password: ")
switches = ["172.16.100.21", "172.16.100.22"]
vlans = [{"id": 10, "name": "DATA"}, {"id": 20, "name": "VOICE"}, {"id": 30, "name": "MGMT"} ]
target_vlans = ["10","20","30"]

def config_vlans(connect):
    cmds = []
    for vlan in vlans:
        cmds += [f"vlan {vlan['id']}", f" name {vlan['name']}"]
    output = connect.send_config_set(cmds)
    print(output)

def connect(switch):
    try:
        device = {
            "device_type": "cisco_ios",
            "host": switch,
            "username": username,
            "password": password,
            "secret": password
        }
        connect = ConnectHandler(**device)
        return connect
    except ConnectionError:
        print(f"Cannot connect to {switch}")
        sys.exit(1)
    except NetmikoTimeoutException:
        print(f"Timeout connecting to {switch}")
        sys.exit(1)
    except NetmikoAuthenticationException:
        print(f"Authentication Error for {switch}")
        sys.exit(1)
    except Exception as e:
        print(f"General Exception for {switch} : {e}")
        sys.exit(1)

def verify_vlans(connect):
    
    parsed_vlans = connect.send_command('show vlan brief', use_textfsm=True)
    #UNDERSTND THIS 
    matched_vlans = [vlan for vlan in parsed_vlans if vlan['vlan_id'] in target_vlans]
    if not matched_vlans:
        print("No matched VLANS")
    for vlan in matched_vlans:
       print(f"VLAN ID: {vlan['vlan_id']} | Name: {vlan['vlan_name']} | Status: {vlan['status']}")
    #pprint.pprint(farts)

def main():
    for switch in switches:
        c = connect(switch)
        config_vlans(c)
        c.save_config()
        verify_vlans(c)
        c.disconnect()

if __name__ == "__main__":
    main()