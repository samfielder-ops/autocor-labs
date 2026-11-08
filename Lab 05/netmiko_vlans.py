"""
connect to both switches, push VLANs 10/20/30 from a Python data structure with
send_config_set , save config, and verify by parsing show vlan brief output. Hand
"""

from netmiko import ConnectHandler 
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

import os, getpass, sys

# Variables
username = os.environ("Enter Username: ")
password = getpass.getpass("Enter Password: ")
switches = ["192.168.100.21", "192.168.100.22"]
vlans = [{"id": 10, "name": "DATA"}, {"id": 20, "name": "VOICE"}, {"id": 30, "name": "MGMT"} ]

def config_vlans(connect):
    cmds = []
    for vlan in vlans:
        cmds += [f"vlan {vlan['id']}", f" name {vlan['name']}"]
    output = connect.send_config_set(cmds)
    print(output)

def connect():
    try:
        for switch in switches:
            device = {
                "platform": "cisco_ios",
                "host": switch,
                "username": username,
                "password": password,
                "secret": password
            }
            connect = ConnectHandler(**device)
            return connect
    except ConnectionError():
        print(f"Cannot connect to {device}")
        sys.exit(1)
    except NetmikoTimeoutException():
        print(f"Timeout connecting to {device}")
        sys.exit(1)
    except NetmikoAuthenticationException():
        print(f"Authentication Error for {device}")
        sys.exit(1)

def verify_vlans(connect):
    farts = connect.parse('show vlan brief')
    for fart in farts:
        if fart['id'] == 10:
            print("Vlan 10 Found")
        elif fart['id'] == 20:
            print("Vlan 20 Found")
        elif fart['id'] == 30:
            print("Vlan 30 Found")
        else:
            continue
            print("VLANS 10, 20, 30 not found")
    print(farts.json())

def main():
    c = connect()
    config_vlans(c)
    c.save_config()
    verify_vlans(c)
    c.disconnect()

if __name__ == "__main__":
    main()