import netmiko
from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException,
	ConnectionException,
    NetmikoAuthenticationException,
)
import getpass

# define variables
username = "admin"
switches = ["172.16.100.21", "172.16.100.22"]
cmds = ["vlan 10", "vlan 20", "vlan 30",]


#connect to both switches & handle auth/ timeout exceptions - narrower than exception
def addVlans():
	password = getpass.getpass("Enter admin password: ")
	for switch in switches:
		device = {
			"device_type": "cisco_ios",
			"host": switch,
			"username": username,
			"password": password
		}
		try:
			with netmiko.ConnectHandler(**device) as connect:
				output = connect.send_config_set(cmds)
				connect.save_config()
				print(output)
#i suspect this part wont work, connect being passed
				result = verify(connect)
				print(result)
		except ConnectionException:
			print("Connection Error")
		except NetmikoAuthenticationException:
			print("Auth Error")
		except NetmikoTimeoutException:
			print("Timeout Error")
		

#Verify with show vlan brief and return
def verify(connect):
	result = connect.send_command("show vlan brief")
	print(result)
	return result

def main():
	addVlans()

if __name__ == "__main__":
	main()