#!/usr/bin/env python3
""" Modbus client """

import argparse
from pymodbus.client  import ModbusTcpClient
from pymodbus.mei_message import ReadDeviceInformationRequest

# ANSI color codes
GREEN = "\033[92m"
RESET = "\033[0m"

def parse_args():
    parser = argparse.ArgumentParser(description="Modbus client")
    parser.add_argument("-i", "--ip", help="Modbus server IP address", required=True)
    parser.add_argument("-p", "--port", help="Modbus server TCP port", type=int, default=502)
    return parser.parse_args()

def display_identity(client):
    request = ReadDeviceInformationRequest()
    response = client.execute(request)

    print(f"{GREEN}Vendor Name : {response.information[0].decode()}")
    print(f"Product Code: {response.information[1].decode()}")
    print(f"Revision    : {response.information[2].decode()}{RESET}")

def main():
    args = parse_args()
    client = ModbusTcpClient(host=args.ip, port=args.port)
    if not client.connect():
        print("❌ Could not connect to Modbus server. Check IP/Port and try again.")
        return

    display_identity(client)
    # TODO: Display menu here
    client.close()

if __name__ == "__main__":
    main()
