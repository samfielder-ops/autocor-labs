"""
nornir_deploy.py with config.yaml , hosts.yaml , groups.yaml : same VLAN push across both switches
concurrently, plus interface descriptions on all six devices, using nornir-netmiko tasks. Print a print_result-style
summary and set a non-zero exit code if any host failed.
"""

from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_config, netmiko_save_config
from nornir.core.task import Task, Result
import getpass, sys

vlan_cmds = ["vlan 10", " name DATA", "vlan 20", " name VOICE", "vlan 30", "name MGMT"]
int_cmds = ["interface Loopback0", " description Nornir Conf"]

def config_push(task: Task, commands: list[str]):
    task.run(task=netmiko_send_config, config_commands=commands)
    task.run(task=netmiko_save_config)
    #run task, push condigf iwth netmiko commands, return result
    return Result(host=task.host, result=f"Applied {len(commands)} lines")

def main():
    #init nornir, set username and pass, filter by cml and run int desc on all, update results
    nornir = InitNornir(config_file="config.yaml")
    nornir.inventory.defaults.password = getpass.getpass("Password: ")
    results = []
    cml = nornir.filter(site="cml")
    if not cml.inventory.hosts:
        print("no hosts matched site=cml", file=sys.stderr)
        return 1
    results.append(cml.run(task=config_push(), name="loopback desc", commands=int_cmds))
    sw = nornir.filter(role="switch")
    if not sw.inventory.hosts:
        print("no hosts matched role=switch", file=sys.stderr)
        return 1
    results.append(sw.run(task=config_push(), name="vlans", commands=vlan_cmds))

    for r in results:
        print_result(r)

    if nornir.data.failed_hosts:
        print(f"FAILED: {sorted(nornir.data.failed_hosts)}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())