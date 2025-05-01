#!/usr/bin/env python3
""" Modbus Client CLI using ANSI colors """

import argparse
import sys
import sqlite3
from getpass import getpass
from pymodbus.client import ModbusTcpClient
from pymodbus.mei_message import ReadDeviceInformationRequest


#this is to chnage the output color to green and red
GREEN = "\033[92m"
RED = "\033[91m"
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



def create_or_update_user(_):
    print("Create or Update User Account")
    username = input("Enter a username: ").strip()
    password = getpass("Enter a password: ").strip()

    if not username or not password:
        print("Username and password cannot be empty.")
        return

    try:
        conn = sqlite3.connect("modbus_db.sqlite")
        cur = conn.cursor()

        # Create tokens table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)

        # Insert or update user
        cur.execute("""
            INSERT INTO tokens (username, password)
            VALUES (?, ?)
            ON CONFLICT(username) DO UPDATE SET password=excluded.password
        """, (username, password))

        conn.commit()
        conn.close()
        print(f"User '{username}' and the associated password added.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")


def read_discrete_input(client):
    print("Discrete Input Contacts [R/O]")
    result = client.read_discrete_inputs(address=0, count=4, slave=1)
    if result.isError():
        print("Unable to read descreet input restart client or server")
    else:
        for i, val in enumerate(result.bits[:4]):
            status = f"{GREEN}True{RESET}" if val else f"{RED}False{RESET}"
            print(f"Contact {i}: {status}")
    

def read_discrete_output_coils(client):
    print("Discrete Output Coils [R/W]")
    result = client.read_coils(address=0, count=4, slave=1)
    if result.isError():
        print("Unable to read output coils. Restart client or server.")
    else:
        for i, val in enumerate(result.bits[:4]):
            status = f"{GREEN}True{RESET}" if val else f"{RED}False{RESET}"
            print(f"Coil {i}: {status}")

def read_analog_input_registers(client):
    print("Analogue Input Registers [R/O]")
    result = client.read_input_registers(address=0, count=8, slave=1)
    if result.isError():
        print("Unable to read analogue input registers.")
    else:
        for i, val in enumerate(result.registers[:8]):
            print(f"Register {i}: {val}")
  

def read_analog_output_registers(client):
    print("Analogue Output Holding Registers [R/W]")
    result = client.read_holding_registers(address=0, count=8, slave=1)
    if result.isError():
        print("Unable to read holding registers.")
    else:
        for i, val in enumerate(result.registers[:8]):
            print(f"Register {i}: {val}")

def read_all_blocks(client):
    print("Display all Discrete and Register values\n")

    # Discrete Inputs
    di = client.read_discrete_inputs(0, 4, slave=1)
    if di.isError():
        print("Discrete Input Contacts       Error reading")
    else:
        contacts = [
            f"{GREEN}True{RESET}" if b else f"{RED}False{RESET}"
            for b in di.bits[:4]
        ]
        print("Discrete Input Contacts       " + ", ".join(contacts))

    # Output Coils
    co = client.read_coils(0, 4, slave=1)
    if co.isError():
        print("Discrete Output Coils         Error reading")
    else:
        coils = [
            f"{GREEN}True{RESET}" if b else f"{RED}False{RESET}"
            for b in co.bits[:4]
        ]
        print("Discrete Output Coils         " + ", ".join(coils))

    # Input Registers
    ir = client.read_input_registers(0, 8, slave=1)
    if ir.isError():
        print("Analogue Input Registers      Error reading")
    else:
        print("Analogue Input Registers      [ " + ", ".join(str(r) for r in ir.registers[:8]) + " ]")

    # Holding Registers
    hr = client.read_holding_registers(0, 8, slave=1)
    if hr.isError():
        print("Analogue Output Holding Registers Error reading")
    else:
        print("Analogue Output Holding Registers [ " + ", ".join(str(r) for r in hr.registers[:8]) + " ]")

def write_output_coils(client):
    print("Enter comma separated")
    user_input = input("list of up to 4 bool values: ").strip()

    try:
        bits_raw = [b.strip() for b in user_input.split(",") if b.strip()]
        if len(bits_raw) != 4:
            print("❌ You must enter exactly 4 values.")
            return

        bits = []
        for b in bits_raw:
            if b not in ['0', '1']:
                raise ValueError
            bits.append(bool(int(b)))

        formatted = ", ".join([f"'{b}'" for b in bits_raw])
        print(f"\nAccepting these values: {formatted}.")



        result = client.write_coils(address=0, values=bits, slave=1)

        if result.isError():
            print("\n to write to coils.")
        else:
            print("\nPost write, Discrete Output Coil values:")
            print(f"Success: {GREEN}True{RESET}\n")
            co = client.read_coils(0, 4, slave=1)
            for i, val in enumerate(co.bits[:4]):
                status = f"{GREEN}True{RESET}" if val else f"{RED}False{RESET}"
                print(f"Coil {i}: {status}")

    except ValueError:
        print("Invalid input. Only comma-separated 0 or 1.")



def write_holding_registers(client):
    print("Enter comma separated")
    print("list of up to 8 integer values: ", end="")
    user_input = input().strip()

    try:
        raw = [v.strip() for v in user_input.split(",") if v.strip()]
        if len(raw) != 8:
            print("You must enter exactly 8 values.")
            return

        values = []
        for val in raw:
            if not val.isdigit() or not (0 <= int(val) <= 9):
                raise ValueError
            values.append(int(val))

        formatted = ", ".join([f"'{v}'" for v in raw])
        print(f"\nAccepting these values: {formatted}.")

        result = client.write_registers(address=0, values=values, slave=1)

        if result.isError():
            print("Failed to write to holding registers.")
        else:
            print("\nPost write, Analogue Output Holding Register values:")
            print("Success:", f"{GREEN}True{RESET}\n")
            hr = client.read_holding_registers(0, 8, slave=1)
            for i, val in enumerate(hr.registers[:8]):
                print(f"Register {i}: {val}")

    except ValueError:
        print("Invalid input. Use only integers from 0 to 9.")



def display_modbus_info(client):


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
    client = ModbusTcpClient(host=args.ip, port=args.port)
    if not client.connect():
        print("Could not connect to Modbus server. Check IP/Port.")
        sys.exit(1)
    display_modbus_info(client)
    while True:  
        print_menu()
        choice = input("\nSelect an activity: ")
        if choice == "1":
            read_discrete_input(client)
        elif choice == "2":
            read_discrete_output_coils(client)   
        elif choice == "3":
            read_analog_input_registers(client)
        elif choice == "4":
            read_analog_output_registers(client)
        elif choice == "5":
            read_all_blocks(client)
        elif choice == "6":
            write_output_coils(client)
        elif choice == "7":
            write_holding_registers(client)
        elif choice == "8":
            create_or_update_user(client)
        elif choice == "9":
            print("\nTerminating client..../n")
            break
        elif choice not in [str(i) for i in range(1, 10)]:
            print("Not a valid choice, try again\n")
        else:
            print(f"You selected option {choice} n")
        input("Main menu, press Enter: ")

if __name__ == "__main__":
    main()
