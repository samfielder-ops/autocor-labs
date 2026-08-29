import getpass
from scrapli.driver.core import IOSXEDriver
from scrapli.exceptions import (
    ScrapliAuthenticationFailed, 
    ScrapliTimeout, 
    ScrapliConnectionError
    )

# define variables
username = "admin"
password = getpass("Enter admin password: ")
switches = ["10.10.20.173", "10.10.20.174"]
cmds = ["vlan 10", "vlan 20", "vlan 30",]

#connect to both switches & handle auth/ timeout exceptions - narrower than exception
def addVlans():
	for switch in switches:
		device = {
			"device_type": "cisco_ios",
			"host": switch,
			"auth_username": username,
			"auth_password": password,
            "auth_strict_key": False,   # skip host-key checking
            "transport": "system",      # or "ssh2", "paramiko", "asyncssh"
		}
		try:
			with IOSXEDriver(**device) as connect:
				output = connect.send_configs(cmds)
				connect.send_command("write memory")
				print(output)
#i suspect this part wont work, connect being passed
				result = verify(connect)
				print(result)
		except ScrapliConnectionError:
			print("Connection Error")
		except ScrapliAuthenticationFailed:
			print("Auth Error")
		except ScrapliTimeout:
			print("Timeout Error")
		

#Verify with show vlan brief and return
def verify(connect):
	result = connect.send_command("show vlan brief",use_textfsm=True)
	print(result)
	return result.json()

def main():
	addVlans()

if __name__ == "__main__":
	main()
