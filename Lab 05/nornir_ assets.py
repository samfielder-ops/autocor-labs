"""
reusing task 3’s config.yaml / hosts.yaml / groups.yaml : one custom grouped
task that runs show version , show inventory and show ip interface brief (TextFSM) on all six devices concurrently
and returns a structured record — hostname, model, serial, IOS version, interface count, uptime. Write report.md
(one table row per device, the same columns as Lab 2’s inventory-report.yml ) and assets.json. A device whose
output fails to parse must be marked failed, not silently skipped. print
_
result summary; non-zero exit if any host
failed.
"""

#imports
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_save_config, netmiko_send_config
from nornir.core.task import Task, Result
import sys, json, os
from pprint import pprint

#variables
password = os.environ.get('PASS')
COLUMNS = ["hostname","model","serial","version","interfaces","uptime"]

#functions
def parse(task, command):
    #run one command with TextFSM
    out = task.run(task=netmiko_send_command, command_string=command, use_textfsm=True).result
    return out

def collect_data(task: Task):
    #variable for each command, parse
    version = parse(task, "show version")[0]
    inventory = parse(task, "show inventory")
    interfaces = parse(task, "show ip interface brief")

    chassis = inventory[0] if inventory else {}
    record = {
        "hostname": version.get("hostname") or task.host.name,
        "model": version.get("hardware") or chassis.get("pid", ""),
        "serial": version.get("serial") or chassis.get("sn", ""),
        "version": version.get("version"),
        "interfaces": len(interfaces),
        "uptime": version.get("uptime")
    }
    return Result(host=task.host, result=record)
                
def report(assets):
    """
    returns a structured record — hostname, model, serial, IOS version, interface count, uptime. Write report.md
    (one table row per device, the same columns as Lab 2’s inventory-report.yml ) and assets.json. A device whose
    output fails to parse must be marked failed, not silently skipped. print
    """
    ##UNDERSTAND THIS
    header = "| " + " | ".join(COLUMNS) + " |"
    rule = "|" + "---|" * len(COLUMNS)
    rows = ["| " + " | ".join(str(a[c]) for c in COLUMNS) + " |" for a in assets]
    with open("report.md","w") as f:
        f.write("\n".join(["# Asset report","", header, rule, *rows, ""]))
    with open("assets.json","w") as f:
        json.dump(assets, f, indent=2)

def main():
    # setup nornir and login
    conn = InitNornir(config_file="config.yaml")
    conn.inventory.defaults.password = password

    #results variable from collect_data and the print
    results = conn.run(task=collect_data)
    #print_result(results)

    #assets variable from sorted results
    assets = sorted(
        #UNDERSTAND THIS
        (multi[0].result for multi in results.values() if not multi.failed), key=lambda a: a["hostname"],
    )
    #write report and print that you did that
    if assets:
        report(assets)
        print(f"Wrote {len(assets)} devices to report.md and assets.json")

    #if report failed, says so and exit
    if results.failed:
        print(f"Failed hosts: {sorted(results.failed_hosts)}")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())