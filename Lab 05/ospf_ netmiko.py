"""
Push OSPF process 1 to R1, R2, and R3 (router-id = Lo0, the 10.0.12.0/30 and 10.0.23.0/30 links and
each loopback, all in area 0) from a Python data structure. Before pushing, read show running-config | section
router ospf and skip any router that already matches. Save config, then verify with show ip ospf neighbor parsed
through TextFSM — R1 and R3 expect one FULL neighbor, R2 expects two. Configure all routers before verifying
anything, and poll with a timeout rather than checking once. Narrow except blocks; non-zero exit if any router
fails
"""

#imports
from netmiko import ConnectHandler
import sys, os, time
from pprint import pprint

#variables
username = os.environ.get('USER')
password = os.environ.get('PASS')


#desired state
ospf = {
    "R1": {
        "host": "172.16.100.11",
        "process": 1,
        "router_id": "1.1.1.1",
        "networks": [("10.0.12.0", "0.0.0.3", 0), ("1.1.1.1", "0.0.0.0", 0)],
        "expected_neighbors": 1
        },
    "R2": {
        "host": "172.16.100.12",
        "process": 1,
        "router_id": "2.2.2.2",
        "networks": [("10.0.12.0", "0.0.0.3", 0),("10.0.23.0", "0.0.0.3", 0), ("2.2.2.2", "0.0.0.0", 0)],
        "expected_neighbors": 2
        },
    "R3": {
        "host": "172.16.100.13",
        "process": 1,
        "router_id": "3.3.3.3",
        "networks": [("10.0.23.0", "0.0.0.3", 0), ("3.3.3.3", "0.0.0.0", 0)],
        "expected_neighbors": 1
        },
    }

#functions
def create_cmds(dev):
    cmds = [
        f"router ospf {dev['process']}", 
        f"router-id {dev['router_id']}", 
        #UNDERSTAND
        *[f"network {n[0]} {n[1]} area {n[2]}" for n in dev['networks']]
        ]
    return cmds

def push_ospf(conn, cmds):
    try:
        result = conn.send_config_set(cmds)
        return result
    except Exception as e:
        print(f"Send Config Failed: {e}")
        sys.exit(1)
        

def check_first(conn, cmds) -> bool:
    #read show running-config | section router ospf and skip any router that 
    # already matches. show running-config | section router ospf 
    try: 
        check = conn.send_command("show running-config | section router ospf")
        running = [line.strip() for line in check.splitlines()]
        #below returns a bool. If all the lines in the acl are fonnd in running _ UNDERSTAND
        return all(cmd.strip() in running for cmd in cmds)
      
    except Exception as e:
        print(f"Check Config Failed: {e}")
        sys.exit(1)

def verify(conn, dev, timeout=10):
    #verify with show ip ospf neighbor parsed through TextFSM — 
    # R1 and R3 expect one FULL neighbor, R2 expects two. Configure 
    # all routers before verifying anything, and poll with a timeout rather than checking once
    deadline = time.time() + timeout  #DOCUMENT
    while time.time() < deadline:

        neighbors = conn.send_command("show ip ospf neighbor", use_textfsm=True)
        #UNDERSTAND
        if isinstance(neighbors, list): 
            full = [n for n in neighbors if n["state"].startswith("FULL") or n["state"].startswith("2WAY")]
            if len(full) == dev["expected_neighbors"]:
                return True
        print("sleeping")
        time.sleep(2)
    return False            

def connection(dev):
    device = {
        "device_type": "cisco_ios",
        "host": dev["host"],
        "username": username,
        "password": password,
        }
    conn = ConnectHandler(**device)
    return conn
#main
def main():
    result = []
    for name, dev in ospf.items():
        
        cmds = create_cmds(dev)
        conn = connection(dev)
        if check_first(conn, cmds) == False:
            print(f"Configuring {name}")
            result.append(push_ospf(conn, cmds))
            conn.save_config()
            conn.disconnect()
        else:
            print(f"OSPF already configured on {name} ...skipping")
    for name, dev in ospf.items():
        if verify(connection(dev), dev) == True:
            print(f"OSPF Established: {name}")
    pprint(result)
    return 0

if __name__ == "__main__":
    sys.exit(main())