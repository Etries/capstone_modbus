#!/usr/bin/env python3
""" Modbus Client CLI using ANSI colors """

import argparse
import sys
from pymodbus.client import ModbusTcpClient
from pymodbus.mei_message import ReadDeviceInformationRequest

#this is to chnage the output color to green and red
GREEN = "\033[92m"
RESET = "\033[0m"

#prints menu
def print_menu():
    print("-" * 40)
    print("1. Discrete Input Contact values")
    print("2. Discrete Output Coil values")
    print("3. Analogue Input Register values")
    print("4. Analogue Output Holding Register values")
    print("5. Display all Discrete and Register values")
    print("6. Write values to the Discrete Output Coils")
    print("7. Write to the Analogue Output Holding Register")
    print("8. Create/update a username and password")
    print("9. Exit/Quit")



def parse_args():
    parser = argparse.ArgumentParser(
        prog="modbus_client.py",
        description="Modbus client",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-i", "--ip", metavar="IP", help="Modbus server IP address")
    parser.add_argument("-p", "--port", metavar="PORT", help="Modbus server TCP port", type=int, default=502)

    args = parser.parse_args()

    if not args.ip:
        parser.print_help()
        sys.exit(1)

    return args


def display_modbus_info(ip, port):
    client = ModbusTcpClient(host=ip, port=port)
    if not client.connect():
        print("Could not connect to Modbus server. Check IP/Port.")
        sys.exit(1)

    request = ReadDeviceInformationRequest()
    response = client.execute(request)

    if not response or not hasattr(response, "information"):
        print("Could not read modbus server information.")
        client.close()
        return None

    print(f"Vendor Name : {GREEN}{response.information[0].decode()}{RESET}")
    print(f"Product Code: {GREEN}{response.information[1].decode()}{RESET}")
    print(f"Revision    : {GREEN}{response.information[2].decode()}{RESET}\n")

    client.close()
    return True



def main():
    args = parse_args()
    display_modbus_info(args.ip, args.port)
    while True:  
        print_menu()
        choice = input("\nSelect an activity: ")

        if choice == "9":
            print("\nTerminating client..../n")
            break
        elif choice not in [str(i) for i in range(1, 10)]:
            print("Not a valid choice, try again\n")
        else:
            print(f"You selected option {choice} n")

if __name__ == "__main__":
    main()
