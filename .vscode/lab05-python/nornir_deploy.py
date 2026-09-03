from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_config, netmiko_save_config
from nornir.core.task import Task, Result
import getpass
import sys

"""
with config.yaml, hosts.yaml, groups.yaml: same VLAN push across both
switches concurrently, plus interface descriptions on all six devices, using nornir-netmiko tasks. Print a
print_result-style summary and set a non-zero exit code if any host failed.
"""
vlan_cmds = ["vlan 10", "vlan 20", "vlan 30",]
int_cmds = ["interface Loopback0", "description Nornir Configured This"]

def push_config(task: Task, commands: list[str]):
     task.run(task=netmiko_send_config, config_commands=commands)
     task.run(task=netmiko_save_config)
     return Result(host=task.host, result=f"applied {len(commands)} lines")

def main():
    nr = InitNornir(config_file="config.yaml")
    nr.inventory.defaults.username = getpass.getuser() 
    nr.inventory.defaults.password = getpass.getpass("Password: ")

    results = []

    cml = nr.filter(site="cml")
    if not cml.inventory.hosts:
        print("no hosts matched site=cml", file=sys.stderr)
        return 1
    print(f"loopback desc -> {list(cml.inventory.hosts)}")
    results.append(cml.run(task=push_config, name="loopback desc", commands=int_cmds))

    sw = nr.filter(role="switch")
    if not sw.inventory.hosts:
        print("no hosts matched role=switch", file=sys.stderr)
        return 1
    print(f"vlans -> {list(sw.inventory.hosts)}")
    results.append(sw.run(task=push_config, name="vlans", commands=vlan_cmds))

    for r in results:
        print_result(r)

    if nr.data.failed_hosts:
        print(f"FAILED: {sorted(nr.data.failed_hosts)}", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
	sys.exit(main())