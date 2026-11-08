"""
Benchmark. Time all three approaches configuring 10 loopbacks per router (use time.perf
counter ). Produce a table: library, lines of code, wall time, error-handling ergonomics
(your subjective 1–5).
"""

#imports
import sys, os, getpass
from netmiko import ConnectHandler
from time import perf_counter
from scrapli import IOSXEDriver
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config


#variables
username = os.environ("Enter Username: ")
password = getpass.getpass("Enter Password: ")
devices = ["192.168.100.11","192.168.100.12","192.168.100.13","192.168.100.21", "192.168.100.22"]
conf_loops = []
for num in range[1,10]:
    conf_loops.append(f"interface loopback{num}")

#functions
def clear_loopbacks() -> bool:
    del_loops = []
    for num in range[1,10]:
        del_loops.append(f"no interface loopback{num}")
    for d in devices:
        dev = {
            "platform": "cisco_ios",
            "host": d,
            "username": username,
            "password": password,
            "secret": password
        }
        try:
            conn = ConnectHandler(**dev)
            conn.send_config_set(del_loops)
            check = conn.send_command("show run | sec interface Loopback")
            if "Loopback" in check:
                print("Loopbacks still present")
                conn.disconnect()
                return False
            else:
                conn.disconnect()
                return True
        except Exception as e:
            print(f"Exception deleting loops: {e}")
            sys.exit(1)

def netmiko_pass():
    for d in devices:
        dev = {
            "platform": "cisco_ios",
            "host": d,
            "username": username,
            "password": password,
            "secret": password
        }
        try:
            conn = ConnectHandler(**dev)
            results = conn.send_config_set(conf_loops)
            return results
        except Exception as e:
            print(f"Exception with Netmiko and loops: {e}")
            sys.exit(1)

def scrapli_pass():
    for d in devices:
        dev = {
            "transport": "system",
            "host": d,
            "auth_username": username,
            "auth_password": password,
            "auth_strict_key": False
        }
        try:
            conn = IOSXEDriver(**dev)
            results = conn.send_commands(conf_loops)
            return results
        except Exception as e:
            print(f"Exception with Scrapli and loops: {e}")
            sys.exit(1)

def nornir_pass():
    try:
        nornir = InitNornir(config="config.yaml")
        results = nornir.run(
            task=netmiko_send_config,
            command_string=conf_loops
        )
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
        netmiko_perf = netmiko_start_time - netmiko_stop_time
        scrapli_start_time = perf_counter()
        results.append(scrapli_pass())
        scrapli_stop_time = perf_counter()
        scrapli_perf = scrapli_start_time - scrapli_stop_time
        nornir_start_time = perf_counter()
        results.append(nornir_pass())
        nornir_stop_time = perf_counter()
        nornir_perf = nornir_start_time - nornir_stop_time
        print(f" Netmiko time: {netmiko_perf:.6f} s", f" Scrapli time: {scrapli_perf:.6f} s",f" Nornir time: {nornir_perf:.6f} s")
        print(results)
        return 0
    else:
        return 1
    
if __name__ == "__main__":
    sys.exit(main())