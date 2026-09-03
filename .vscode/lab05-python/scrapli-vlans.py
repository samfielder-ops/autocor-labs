import getpass
from scrapli.driver.core import IOSXEDriver
from scrapli.exceptions import (
    ScrapliAuthenticationFailed, 
    ScrapliTimeout, 
    ScrapliConnectionError,
	ScrapliException
    )

# define variables
username = "admin"
switches = ["172.16.100.21", "172.16.100.22"]
cmds = ["vlan 10", "vlan 20", "vlan 30",]

#connect to both switches & handle auth/ timeout exceptions - narrower than exception
def addVlans():
	password = getpass.getpass("Enter admin password: ")
	for switch in switches:
		device = {
			"host": switch,
			"auth_username": username,
			"auth_password": password,
            "auth_strict_key": False,   # skip host-key checking
            "transport": "system",      # or "ssh2", "paramiko", "asyncssh"
		}
		try:
			with IOSXEDriver(**device) as connect:
				connect.send_configs(cmds)
				connect.send_command("write memory")
				result = verify(connect)
				print(result)
		
		except ScrapliConnectionError:
			print("Connection Error")
		except ScrapliAuthenticationFailed:
			print("Auth Error")
		except ScrapliTimeout:
			print("Timeout Error")
		except ScrapliException as e:
			print(f"Connection Error {e}")
		

#Verify with show vlan brief and return
def verify(connect):
	result = connect.send_command("show vlan brief")
	structured_result = result.textfsm_parse_output()
	return structured_result

def main():
	addVlans()

if __name__ == "__main__":
	main()
