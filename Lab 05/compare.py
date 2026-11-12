"""
Benchmark. Time all three approaches configuring 10 loopbacks per router (use time.perf
counter ). Produce a table: library, lines of code, wall time, error-handling ergonomics
(your subjective 1–5).
"""

#imports
import sys, os
from netmiko import ConnectHandler
from time import perf_counter
from scrapli.driver.core import IOSXEDriver
from scrapli import Scrapli
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config
from pprint import pprint


#variables
username = os.environ.get('USER')
password = os.environ.get('PASS')
devices = ["172.16.100.11","172.16.100.12","172.16.100.13","172.16.100.21", "172.16.100.22"]
conf_loops = []
for num in range(1,11):
    conf_loops.append(f"interface loopback{num}")

#functions
def clear_loopbacks() -> bool:
    del_loops = []
    for num in range(11):
        del_loops.append(f"no interface loopback{num}")
    for d in devices:
        dev = {
            "device_type": "cisco_ios",
            "host": d,
            "username": username,
            "password": password,
            "secret": password
        }
        try:
            conn = ConnectHandler(**dev)
            conn.send_config_set(del_loops)
            print(f" Deleted Loops on {d}")
            check = conn.send_command("show run | sec interface Loopback")
            if "Loopback" in check:
                print(f"Loopbacks on {d} still present")
                conn.disconnect()
                return False
            else:
                conn.disconnect()
        except Exception as e:
            print(f"Exception deleting loops: {e}")
            sys.exit(1)
    return True

def netmiko_pass():
    results = []
    for d in devices:
        dev = {
            "device_type": "cisco_ios",
            "host": d,
            "username": username,
            "password": password,
            "secret": password
        }
        try:
            conn = ConnectHandler(**dev)
            results.append (conn.send_config_set(conf_loops))
            print(f"Netmiko configured loops on {d}")
        except Exception as e:
            print(f"Exception with Netmiko and loops: {e}")
            sys.exit(1)
    return results
def scrapli_pass():
    results = []
    for d in devices:
        dev = {
            "transport": "paramiko",
            "host": d,
            "auth_username": username,
            "auth_password": password,
            "auth_secondary": password,
            "auth_strict_key": False
        }
        try:
            conn = IOSXEDriver(**dev)
            conn.open()
            results.append(conn.send_commands(conf_loops))
            print(f"Scrapli configured loops on {d}")
            #conn.close()

        except Exception as e:
            print(f"Exception with Scrapli and loops on {d}: {e} ")
            sys.exit(1)
    return results

def nornir_pass():
    try:
        nornir = InitNornir(config_file="config.yaml")
        nornir.inventory.defaults.password = password
        results = nornir.run(
            task=netmiko_send_config,
            command_string=conf_loops
        )
        print(f"Nornir configured loops")
        return results
    except Exception as e:
        print(f"Exception with Nornir and loops: {e}")
        sys.exit(1)

#main
def main():
    if clear_loopbacks() == True:
        results = []
        netmiko_start_time = perf_counter()
        results.append(netmiko_pass())
        netmiko_stop_time = perf_counter()
        netmiko_perf = netmiko_stop_time - netmiko_start_time
    if clear_loopbacks() == True:
        scrapli_start_time = perf_counter()
        results.append(scrapli_pass())
        scrapli_stop_time = perf_counter()
        scrapli_perf = scrapli_stop_time- scrapli_start_time
    if clear_loopbacks() == True:
        nornir_start_time = perf_counter()
        results.append(nornir_pass())
        nornir_stop_time = perf_counter()
        nornir_perf = nornir_stop_time - nornir_start_time
        print(f" \r\r\rNetmiko time: {netmiko_perf:.3f}s", f" Scrapli time: {scrapli_perf:.3f}s",f" Nornir time: {nornir_perf:.3f}s\r\r\r")
        pprint(results)
        return 0
    else:
        return 1
    
if __name__ == "__main__":
    sys.exit(main())