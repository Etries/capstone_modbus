#!/usr/bin/env python3

""" This is a modbus client module that will try
to connect to the modbus server based on the ip and 
port provided. after a successful connection it will 
CLI based interactive men option to read and write
to the modbus server"""

import argparse
import sys
import os
import sqlite3
from getpass import getpass
from pymodbus.client import ModbusTcpClient
from pymodbus.mei_message import ReadDeviceInformationRequest


#this is to chnage the output color to green and red
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "modbus_db.sqlite")

#Display menus options
def display_menu():
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

#parses the given argument in CLI
def args_parser():
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
    if not args.port:
        parser.print_help()
        sys.exit(1)

    return args


def save_modbus_state(ip, di, co, ir, hr):
    """This function is called to save the modbus status
        from server at first session creation"""

    try:
        
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS modbus (
                ip TEXT PRIMARY KEY,
                di TEXT,
                co TEXT,
                ir TEXT,
                hr TEXT
            )
        """)
        cur.execute("""
            INSERT INTO modbus (ip, di, co, ir, hr)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(ip) DO UPDATE SET
                di=excluded.di,
                co=excluded.co,
                ir=excluded.ir,
                hr=excluded.hr
        """, (ip, di, co, ir, hr))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error saving Modbus state: {e}")

def save_modbus_field(ip, field, value):
    """Saves the fields and update dabase at
    write function to the server
    """


    if field not in ["di", "co", "ir", "hr"]:
        print(f"Invalid Modbus field: {field}")
        return

    try:
        conn = sqlite3.connect("modbus_db.sqlite")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS modbus (
                ip TEXT PRIMARY KEY,
                di TEXT,
                co TEXT,
                ir TEXT,
                hr TEXT
            )
        """)
        cur.execute("SELECT ip FROM modbus WHERE ip = ?", (ip,))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO modbus (ip) VALUES (?)", (ip,))
        cur.execute(f"UPDATE modbus SET {field} = ? WHERE ip = ?", (value, ip))
        conn.commit()
        conn.close()
       
    except sqlite3.Error as e:
        print(f"Error updating {field}: {e}")

def create_user(_):
    """creates user and save it to databse
    if user is already created, it will update
    the password"""


    print("Create or Update User Account")
    username = input("Enter a username: ").strip()
    password = getpass("Enter a password: ").strip()

    if not username or not password:
        print("Username and password cannot be empty.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)

        
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


def initial_modbus_sync(client, ip):
    """This is the initial function that
    will run ass soon as connected to modbus
    server to save current seeson of server"""

    try:
        di = client.read_discrete_inputs(0, 4, slave=1)
        co = client.read_coils(0, 4, slave=1)
        ir = client.read_input_registers(0, 8, slave=1)
        hr = client.read_holding_registers(0, 8, slave=1)

        if any(block.isError() for block in [di, co, ir, hr]):
            print("Warning: One or more Modbus blocks failed during initial sync.")
            return

        save_modbus_state(
            ip=ip,
            di=",".join(["1" if b else "0" for b in di.bits[:4]]),
            co=",".join(["1" if b else "0" for b in co.bits[:4]]),
            ir=",".join(str(r) for r in ir.registers[:8]),
            hr=",".join(str(r) for r in hr.registers[:8])
        )
    except Exception as e:
        print(f"Modbus sync failed: {e}")


def read_discrete_input(client):
    """a function to read discree input from
    server"""


    print("Discrete Input Contacts [R/O]")
    result = client.read_discrete_inputs(address=0, count=4, slave=1)
    if result.isError():
        print("Unable to read descreet input restart client or server")
    else:
        for i, val in enumerate(result.bits[:4]):
            status = f"{GREEN}True{RESET}" if val else f"{RED}False{RESET}"
            print(f"Contact {i}: {status}")

#reads coils status from server    
def read_output_coils(client):

    print("Discrete Output Coils [R/W]")
    result = client.read_coils(address=0, count=4, slave=1)
    if result.isError():
        print("Unable to read output coils. Restart client or server.")
    else:
        for i, val in enumerate(result.bits[:4]):
            status = f"{GREEN}True{RESET}" if val else f"{RED}False{RESET}"
            print(f"Coil {i}: {status}")

#Retrieves input registers from the modbus server
def read_input_registers(client):
    print("Analogue Input Registers [R/O]")
    result = client.read_input_registers(address=0, count=8, slave=1)
    if result.isError():
        print("Unable to read analogue input registers.")
    else:
        for i, val in enumerate(result.registers[:8]):
            print(f"Register {i}: {val}")


#Retrieves holding registers from the modbus server
def read_holding_registers(client):
    print("Analogue Output Holding Registers [R/W]")
    result = client.read_holding_registers(address=0, count=8, slave=1)
    if result.isError():
        print("Unable to read holding registers.")
    else:
        for i, val in enumerate(result.registers[:8]):
            print(f"Register {i}: {val}")

#Retrieves all status from modbus server
def read_all_blocks(client):

    print("Display all Discrete and Register values\n")
    di = client.read_discrete_inputs(0, 4, slave=1)
    if di.isError():
        print("Discrete Input Contacts Error reading")
    else:
        contacts = [
            f"{GREEN}True{RESET}" if b else f"{RED}False{RESET}"
            for b in di.bits[:4]
        ]
        print("Discrete Input Contacts" + ", ".join(contacts))

        co = client.read_coils(0, 4, slave=1)
    if co.isError():
        print("Discrete Output Coils/t Error reading")
    else:
        coils = [
            f"{GREEN}True{RESET}" if b else f"{RED}False{RESET}"
            for b in co.bits[:4]
        ]
        print("Discrete Output Coils/t" + ", ".join(coils))

    ir = client.read_input_registers(0, 8, slave=1)
    if ir.isError():
        print("Analogue Input Registers/tError reading")
    else:
        print("Analogue Input Registers/t[ " + ", ".join(str(r) for r in ir.registers[:8]) + " ]")
        hr = client.read_holding_registers(0, 8, slave=1)
    if hr.isError():
        print("Analogue Output Holding Registers Error reading")
    else:
        print("Analogue Output Holding Registers [ " + ", ".join(str(r) for r in hr.registers[:8]) + " ]")


#recieves inputs and write to server
def write_output_coils(client, ip):
    """This will accept input from user
    first validates then write to server"""
    
    print("Enter comma separated 0s and 1s ")
    user_input = input("list of up to 4 bool values: ").strip()

    try:
        bits_raw = [b.strip() for b in user_input.split(",") if b.strip()]
        if len(bits_raw) != 4:
            print("You must enter exactly 4 values.")
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
            print("\n failed to write to coils.")
        else:
            print("\nPost write, Discrete Output Coil values:")
            print(f"Success: {GREEN}True{RESET}\n")
            save_modbus_field(ip, "co", ",".join(map(str, map(int, bits))))
            co = client.read_coils(0, 4, slave=1)
            for i, val in enumerate(co.bits[:4]):
                status = f"{GREEN}True{RESET}" if val else f"{RED}False{RESET}"
                print(f"Coil {i}: {status}")

    except ValueError:
        print("Invalid input. Only comma-separated 0 or 1.")

#recieves inputs and write to server
def write_holding_registers(client,ip):
    """This will accept input from user
    first validates then write to server"""

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
            save_modbus_field(ip, "hr", ",".join(map(str, values)))
            hr = client.read_holding_registers(0, 8, slave=1)
            for i, val in enumerate(hr.registers[:8]):
                print(f"Register {i}: {val}")

    except ValueError:
        print("Invalid input. Use only integers from 0 to 9.")

#This will display modbus info at the start
def display_modbus_info(client):


    request = ReadDeviceInformationRequest()
    response = client.execute(request)

    if not response or not hasattr(response, "information"):
        print("Unable to read Modbus device info.")
        client.close()
        return None
    #colour will be applied to the output to show what is on and off
    print(f"Vendor Name : {GREEN}{response.information[0].decode()}{RESET}")
    print(f"Product Code: {GREEN}{response.information[1].decode()}{RESET}")
    print(f"Revision    : {GREEN}{response.information[2].decode()}{RESET}\n")

    client.close()
    return True

def main():
    """"main function"""

    args = args_parser()
    ip = args.ip
    port = args.port
    client = ModbusTcpClient(host=ip, port=port)
    if not client.connect():
        print("Could not connect to Modbus server. Check IP/Port.")
        sys.exit(1)
    initial_modbus_sync(client, args.ip)
    display_modbus_info(client)
    while True:  
        display_menu()  # calls the display funcion
        choice = input("\nSelect an activity: ")
        if choice == "1":
            read_discrete_input(client)
        elif choice == "2":
            read_output_coils(client)   
        elif choice == "3":
            read_input_registers(client)
        elif choice == "4":
            read_holding_registers(client)
        elif choice == "5":
            read_all_blocks(client)
        elif choice == "6":
            write_output_coils(client,ip)
        elif choice == "7":
            write_holding_registers(client,ip)
        elif choice == "8":
            create_user(client)
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
