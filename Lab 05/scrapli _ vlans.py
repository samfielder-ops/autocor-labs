import os, sys, getpass
from scrapli import IOSXEDriver
from scrapli.exceptions import (
    ScrapliAuthenticationFailed,
    ScrapliTimeout,
    ScrapliConnectionError,
    ScrapliException
)

#variables
username = os.environ("Enter Username: ")
password = getpass.getpass("Enter Password: ")
switches = ["192.168.100.21", "192.168.100.22"]
vlans = [{"id": 10, "name": "DATA"}, {"id": 20, "name": "VOICE"}, {"id": 30, "name": "MGMT"}]

def connect():
    try:
        for s in switches:
            device = {
                "transport": "system",
                "host": s,
                "auth_username": username,
                "auth_password": password,
                "auth_strict_key": False
            }
            con = IOSXEDriver(**device)
            return con
    except ScrapliAuthenticationFailed:
        print(f"Authentication Failure on {device}")
    except ScrapliTimeout:
        print(f"Timeout on {device}")
    except ScrapliConnectionError:
        print(f"Connection Failure on {device}")

def configure_vlans(con):
    cmds = []
    for v in vlans:
        cmds += [f"vlan {v['id']}", f" name {v['name']}"]
    config = con.send_commands(cmds)
    print(config)

def verify_vlans(con):
    result = con.send_command("show vlan brief")
    structured_result = result.textfsm_parse_output()
    return structured_result

def main():
    connect = connect()
    configure_vlans(connect)
    connect.send_command("write memory")
    result = verify_vlans(connect)
    print(result)
    connect.close()
    pass

if __name__ == "__main__":
    main()