"""
Pick one library and push the MGMT-IN ACL from Lab 2’s data model. The script must be idempotent
by construction: read current ACL first, diff against intent, push only if different.

MGMT-IN : permit 192.168.100.0/24 to any on 22 and 443, deny any log

Make a before one do diff against one. And apply to an interface.
"""
#imports
from scrapli import IOSXEDriver 
import os, sys, getpass

#variables
username = os.environ("Enter Username: ")
password = getpass.getpass("Enter Password: ")
switches = ["192.168.100.21", "192.168.100.22"]

new_acl = [
    "ip access-list extended MGMT", 
    " permit tcp 192.168.100.0 255.255.255.0 eq 22",
    " permit tcp 192.168.100.0 255.255.255.0 eq 443",
    " deny any any log"
    ]

# functions
def check_acl(conn) -> bool:
    try:
        check = conn.send_command("show running-config | sec ip access-list extended MGMT", use_textFSM=True)
        if check == new_acl:
            return True
        else:
            return False
    except Exception as e:
        print(f"Exception checking device: {e}")
        sys.exit(1)

def config_acl(conn):
    try:
        result = conn.send_commands(new_acl)
        return result
    except Exception as e:
        print(f"Exception configuring device: {e}")
        sys.exit(1)

#main
def main():
    for s in switches:
        device = {
            "transport": "system",
            "host": s,
            "auth_username": username,
            "auth_password": password,
            "auth_strict_key": False
            }
        conn = IOSXEDriver(**device)
        if check_acl(conn) == False:
            result = config_acl(conn)
            print(result)
            return 0
        else:
            print(f"ACL already configured on {device}")
            return 2
    return 0

#init main - make this a habit
if __name__ == "__main__":
    sys.exit(main())