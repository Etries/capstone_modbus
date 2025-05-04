#!/usr/bin/env python3

import tkinter as tk
import os
import sqlite3
from getpass import getpass
from pymodbus.client import ModbusTcpClient
from pymodbus.mei_message import ReadDeviceInformationRequest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "modbus_db.sqlite")

# Setting up the GUI frames
root = tk.Tk()
root.title("Modbus Client GUI")
root.geometry("900x500") 
client = None 
connection_frame = tk.Frame(root, bg="#dfe6e9")
connection_frame.pack(fill="x", padx=10, pady=5)

tk.Label(connection_frame, text="Host/IP:", bg="#dfe6e9").pack(side="left", padx=(10, 2))
ip_entry = tk.Entry(connection_frame)
ip_entry.insert(0, "127.0.0.1")
ip_entry.pack(side="left")

tk.Label(connection_frame, text="Port:", bg="#dfe6e9").pack(side="left", padx=(10, 2))
port_entry = tk.Entry(connection_frame, width=6)
port_entry.insert(0, "502")
port_entry.pack(side="left")

status = tk.Label(connection_frame, text="Not connected!!!", fg="red", bg="#dfe6e9")
status.pack(side="right", padx=10)

modbus_info = tk.Label(root, text="", font=("Arial", 10), bg="#e5e5e5", anchor="w")
modbus_info.pack(fill="x", side="bottom", padx=10, pady=3)
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)
navbar_frame = tk.Frame(main_frame, width=200, bg="#1a2b4c")
navbar_frame.pack(side="left", fill="y")
content_frame = tk.Frame(main_frame, bg="#f0f0f0")
content_frame.pack(side="right", expand=True, fill="both")


def save_modbus_field(ip, field, value):
    if field not in ["di", "co", "ir", "hr"]:
        return
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
        cur.execute("SELECT ip FROM modbus WHERE ip = ?", (ip,))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO modbus (ip) VALUES (?)", (ip,))
        cur.execute(f"UPDATE modbus SET {field} = ? WHERE ip = ?", (value, ip))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        tk.Label(content_frame, text=f"Database error: {e}", fg="red", bg="#f0f0f0").pack()

def create_user():
    for widget in content_frame.winfo_children():
        widget.destroy()

    title = tk.Label(content_frame, text="Create or Update User", font=("Arial", 14), bg="#f0f0f0")
    title.pack(pady=10)
    tk.Label(content_frame, text="Username:", bg="#f0f0f0").pack(pady=(10, 0))
    username_entry = tk.Entry(content_frame)
    username_entry.pack()
    tk.Label(content_frame, text="Password:", bg="#f0f0f0").pack(pady=(10, 0))
    password_entry = tk.Entry(content_frame, show="*")
    password_entry.pack()

    def submit():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            tk.Label(content_frame, text="Username and password cannot be empty.", fg="red", bg="#f0f0f0").pack()
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
            tk.Label(content_frame, text=f"User '{username}' added/updated.", fg="green", bg="#f0f0f0").pack()

        except sqlite3.Error as e:
            tk.Label(content_frame, text=f"Database error: {e}", fg="red", bg="#f0f0f0").pack()

    submit_btn = tk.Button(content_frame, text="Submit", command=submit)
    submit_btn.pack(pady=10)

def read_discrete_inputs():
    for widget in content_frame.winfo_children():
        widget.destroy()

    title = tk.Label(content_frame, text="Discrete Inputs [Read Only]", font=("Arial", 14), bg="#f0f0f0")
    title.pack(pady=10)

    if client is None:
        tk.Label(content_frame, text="⚠️ Not connected", fg="orange", bg="#f0f0f0").pack()
        return

    result = client.read_discrete_inputs(address=0, count=4, slave=1)
    if result.isError():
        tk.Label(content_frame, text="Failed to read discrete inputs.", fg="red", bg="#f0f0f0").pack()
    else:
        bits = result.bits[:4]
        for i, bit in enumerate(bits):
            color = "green" if bit else "red"
            status = "True" if bit else "False"
            tk.Label(content_frame, text=f"Contact {i}: {status}", fg=color, font=("Arial", 12), bg="#f0f0f0").pack()

def read_output_coils():
    for widget in content_frame.winfo_children():
        widget.destroy()

    title = tk.Label(content_frame, text="Output Coils [Read Only]", font=("Arial", 14), bg="#f0f0f0")
    title.pack(pady=10)

    if client is None:
        tk.Label(content_frame, text="Not connected to any Modbus server.", fg="orange", bg="#f0f0f0").pack()
        return

    result = client.read_coils(address=0, count=4, slave=1)
    if result.isError():
        tk.Label(content_frame, text="Failed to read output coils.", fg="red", bg="#f0f0f0").pack()
    else:
        bits = result.bits[:4]
        for i, bit in enumerate(bits):
            color = "green" if bit else "red"
            status = "True" if bit else "False"
            tk.Label(content_frame, text=f"Coil {i}: {status}", fg=color, font=("Arial", 12), bg="#f0f0f0").pack()

def read_input_registers():
    for widget in content_frame.winfo_children():
        widget.destroy()

    title = tk.Label(content_frame, text="Input Registers [Read Only]", font=("Arial", 14), bg="#f0f0f0")
    title.pack(pady=10)

    if client is None:
        tk.Label(content_frame, text="Not connected to any Modbus server.", fg="orange", bg="#f0f0f0").pack()
        return

    result = client.read_input_registers(address=0, count=8, slave=1)
    if result.isError():
        tk.Label(content_frame, text="Failed to read input registers.", fg="red", bg="#f0f0f0").pack()
    else:
        values = result.registers[:8]
        for i, val in enumerate(values):
            tk.Label(content_frame, text=f"Register {i}: {val}", font=("Arial", 12), bg="#f0f0f0").pack()

def read_holding_registers():
    for widget in content_frame.winfo_children():
        widget.destroy()

    title = tk.Label(content_frame, text="Holding Registers [Read Only]", font=("Arial", 14), bg="#f0f0f0")
    title.pack(pady=10)

    if client is None:
        tk.Label(content_frame, text="Not connected to any Modbus server.", fg="orange", bg="#f0f0f0").pack()
        return

    result = client.read_holding_registers(address=0, count=8, slave=1)
    if result.isError():
        tk.Label(content_frame, text="Failed to read holding registers.", fg="red", bg="#f0f0f0").pack()
    else:
        values = result.registers[:8]
        for i, val in enumerate(values):
            tk.Label(content_frame, text=f"Register {i}: {val}", font=("Arial", 12), bg="#f0f0f0").pack()

def connect_to_server():
    global client, current_ip
    ip = ip_entry.get()
    port = int(port_entry.get())
    current_ip = ip

    try:
        client = ModbusTcpClient(host=ip, port=port)
        if client.connect():
            status.config(text=f"Connected to {ip}:{port}", fg="green")

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
                CREATE TABLE IF NOT EXISTS tokens (
                    username TEXT PRIMARY KEY,
                    password TEXT
                )
            """)
            conn.commit()
            conn.close()

            try:
                info_request = ReadDeviceInformationRequest()
                info_response = client.execute(info_request)

                if not info_response.isError():
                    vendor = info_response.information[0].decode()
                    product = info_response.information[1].decode()
                    revision = info_response.information[2].decode()

                    modbus_info.config(
                        text=f"Vendor: {vendor} | Product: {product} | Revision: {revision}",
                        fg="black"
                    )
                else:
                    modbus_info.config(text="Unable to read Modbus device info.", fg="red")
            except Exception as info_err:
                modbus_info.config(text=f"Modbus info error: {info_err}", fg="red")

        else:
            status.config(text="Connection failed", fg="red")
            modbus_info.config(text="")
    except Exception as e:
        status.config(text=f"Error: {e}", fg="red")
        modbus_info.config(text="")

def write_output_coils():
    for widget in content_frame.winfo_children():
        widget.destroy()

    title = tk.Label(content_frame, text="Write to Output Coils", font=("Arial", 14), bg="#f0f0f0")
    title.pack(pady=10)

    if client is None:
        tk.Label(content_frame, text="Not connected to any Modbus server.", fg="orange", bg="#f0f0f0").pack()
        return

    result = client.read_coils(address=0, count=4, slave=1)
    if result.isError():
        tk.Label(content_frame, text="Failed to read current coil states.", fg="red", bg="#f0f0f0").pack()
        return

    current_bits = result.bits[:4]
    coil_vars = []

    def submit():
        bits = [bool(var.get()) for var in coil_vars]
        result = client.write_coils(address=0, values=bits, slave=1)
        if result.isError():
            tk.Label(content_frame, text="Failed to write to coils.", fg="red", bg="#f0f0f0").pack()
        else:
            tk.Label(content_frame, text="Coil values written successfully.", fg="green", bg="#f0f0f0").pack()
            save_modbus_field(current_ip, "co", ",".join(map(str, map(int, bits))))

    for i, bit in enumerate(current_bits):
        var = tk.IntVar(value=int(bit))
        coil_vars.append(var)

        frame = tk.Frame(content_frame, bg="#f0f0f0")
        frame.pack(pady=2, anchor="w")

        tk.Label(frame, text=f"Coil {i}:", bg="#f0f0f0").pack(side="left", padx=5)
        tk.Radiobutton(frame, text="False", variable=var, value=0, bg="#f0f0f0").pack(side="left")
        tk.Radiobutton(frame, text="True", variable=var, value=1, bg="#f0f0f0").pack(side="left")

    submit_btn = tk.Button(content_frame, text="Submit", command=submit)
    submit_btn.pack(pady=10)

def write_holding_registers():
    for widget in content_frame.winfo_children():
        widget.destroy()

    title = tk.Label(content_frame, text="Write to Holding Registers", font=("Arial", 14), bg="#f0f0f0")
    title.pack(pady=10)

    if client is None:
        tk.Label(content_frame, text="Not connected to any Modbus server.", fg="orange", bg="#f0f0f0").pack()
        return

    result = client.read_holding_registers(address=0, count=8, slave=1)
    if result.isError():
        tk.Label(content_frame, text="Failed to read current holding registers.", fg="red", bg="#f0f0f0").pack()
        return

    current_values = result.registers[:8]
    entry_vars = []

    def submit():
        values = []
        for i, var in enumerate(entry_vars):
            raw = var.get().strip()
            if not raw.isdigit():
                tk.Label(content_frame, text=f"Invalid input at Register {i}: must be an integer 0–9.", fg="red", bg="#f0f0f0").pack()
                return
            val = int(raw)
            if not (0 <= val <= 9):
                tk.Label(content_frame, text=f"Value out of range at Register {i}: only 0–9 allowed.", fg="red", bg="#f0f0f0").pack()
                return
            values.append(val)

        while len(values) < 8:
            values.append(0)

        result = client.write_registers(address=0, values=values, slave=1)
        if result.isError():
            tk.Label(content_frame, text="Failed to write to holding registers.", fg="red", bg="#f0f0f0").pack()
        else:
            tk.Label(content_frame, text="Holding register values written successfully.", fg="green", bg="#f0f0f0").pack()
            save_modbus_field(current_ip, "hr", ",".join(map(str, values)))

    for i, val in enumerate(current_values):
        frame = tk.Frame(content_frame, bg="#f0f0f0")
        frame.pack(pady=2, anchor="w")

        tk.Label(frame, text=f"Register {i}:", bg="#f0f0f0").pack(side="left", padx=5)
        var = tk.StringVar(value=str(val))
        entry = tk.Entry(frame, width=6, textvariable=var)
        entry.pack(side="left")
        entry_vars.append(var)

    submit_btn = tk.Button(content_frame, text="Submit", command=submit)
    submit_btn.pack(pady=10)


buttons = [
    ("Read Discrete Inputs", read_discrete_inputs),
    ("Read Output Coils", read_output_coils),
    ("Read Input Registers", read_input_registers),
    ("Read Holding Registers", read_holding_registers),
    ("Write Output Coils", write_output_coils),
    ("Write Holding Registers", write_holding_registers),
    ("Create User", create_user),
    ("Exit", root.quit)
]

for label, cmd in buttons:
    btn = tk.Button(navbar_frame, text=label, command=cmd, bg="#2c3e50", fg="white", relief="flat")
    btn.pack(fill="x", pady=2, padx=5, ipady=5)
connect_btn = tk.Button(connection_frame, text="Connect", command=connect_to_server)
connect_btn.pack(side="left", padx=10)

root.mainloop()
