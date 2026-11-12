"""
Pick one library and push the MGMT-IN ACL from Lab 2’s data model. The script must be idempotent
by construction: read current ACL first, diff against intent, push only if different.

MGMT-IN : permit 192.168.100.0/24 to any on 22 and 443, deny any log

Make a before one do diff against one. And apply to an interface.
"""
#imports
import scrapli
from scrapli.driver.core import IOSXEDriver 
import os, sys, re
from pprint import pprint

#variables
username = os.environ.get('USER')
password = os.environ.get('PASS')
switches = ["172.16.100.21", "172.16.100.22"]

new_acl = [
    "ip access-list extended MGMT", 
    "permit tcp 192.168.100.0 0.0.0.255 any eq 22",
    "permit tcp 192.168.100.0 0.0.0.255 any eq 443",
    "deny ip any any log"
    ]

# functions
def check_acl(conn) -> bool:
    try:
        resp = conn.send_command("show running-config | sec ip access-list extended MGMT")
        ##UNDERSTAND THIS - strip out the seq numbers
        running = [re.sub(r"^\d+\s+", "",line.strip()) for line in resp.result.splitlines()]
        #below returns a bool. If all the lines in the acl are fonnd in running
        return all(line.strip() in running for line in new_acl)
    except Exception as e:
        print(f"Exception checking device: {e}")
        sys.exit(1)

def config_acl(conn):
    try:
        result = conn.send_configs(new_acl)
        conn.send_command("write memory")
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
        conn.open()
        if not check_acl(conn):
            print(f"{s}: ACL Not present or does not match...configuring...")
            config_acl(conn)
        else:
            print(f"{s}: ACL already configured")
        conn.close()
        #if the return code is inside the if else, then it doesnt go to teh next in the for loop
    return 0

#init main - make this a habit
if __name__ == "__main__":
    sys.exit(main())