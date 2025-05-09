#!/usr/bin/env python3
""" Pymodbus Server """

__author__ = "James Garland Diarmuid O'Briain"
__copyright__ = "Copyright 2024, SETU"
__licence__ = "European Union Public Licence v1.2"
__version__ = "3.0"

# Install Python modules pyModbus and twisted
#
# ~$ python3 -m pip install pyModbus twisted pyyaml
# ~$ sudo python3 -m pip install pyModbus twisted pyyaml

import os
import sys
import yaml
import socket
from pymodbus.version import version
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

remote_ip = "0.0.0.0"
port = 502
euid = os.geteuid()
addr = dict()
file = "blockdata_init.yaml"

label_dict = {
    "di": "Discrete Input Contacts",
    "co": "Discrete Output Coils",
    "ir": "Analogue Input Register",
    "hr": "Analogue Output Holding Register"
}

block_count = {"di": 4, "co": 4, "ir": 8, "hr": 8}

# // Get the local IP address //
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)


def get_blockdata():
    dict_ = dict()

    if not os.path.exists(file):
        err = 1
        dict_["di"] = (0, [0] * 5)  # (0-False, 1-True)
        dict_["co"] = (0, [0] * 5)  # (0-False, 1-True)
        dict_["ir"] = (0, [0] * 9)
        dict_["hr"] = (0, [0] * 9)
    else:
        # // De-serialise data from the file (read it) //
        err = 0
        print(f"De-serialising data from '{file}'")
        try:
            with open(file, mode="r") as fh:
                yaml_in = yaml.load(fh, Loader=yaml.FullLoader)
                for k, v in yaml_in.items():
                    dict_[k] = (0, [0, *v])
        except:
            print(f"ERROR: YAML file format error in {file}")

    return err, dict_


def clear_shell():
    """Identify the shell type and clear"""

    cmd = "cls" if os.name in ("nt", "dos") else "clear"
    os.system(cmd)
    return 0


def sudo_switch():
    """Make Server run as sudo"""
    args = ["sudo", sys.executable] + sys.argv + [os.environ]
    # // Switch current running process with the sudo //
    print("Switching to root privileges as euid: 0")
    os.execlpe("sudo", *args)
    return 0


def run_pymodbus_server(err, addr):
    """Run the pyModbus Server"""

    # // Create a datastore and populate it with test data //
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(*addr["di"]),
        co=ModbusSequentialDataBlock(*addr["co"]),
        ir=ModbusSequentialDataBlock(*addr["ir"]),
        hr=ModbusSequentialDataBlock(*addr["hr"]),
    )

    context = ModbusServerContext(slaves=store, single=True)

    # // Populate the Modbus server information fields //
    # // these return as response to identity queries  //
    identity = ModbusDeviceIdentification()
    identity.VendorName = "SETU Modbus Laboratory"
    identity.ProductCode = "PM"
    identity.VendorUrl = "https://pymodbus.readthedocs.io/"
    identity.ProductName = "Modbus Server"
    identity.ModelName = "Python Modbus"
    identity.MajorMinorRevision = "2.0"

    # // Print the initial State //
    clear_shell()
    print()
    print(
        f"  Vendor Name : {identity.VendorName}\n",
        f" Vendor URL  : {identity.VendorUrl}\n",
        f" Product Name: {identity.ProductName}\n",
        f" Model Name  : {identity.ModelName}\n",
        f" Revision    : {identity.MajorMinorRevision}",
    )
    print()
    print(f"  Initial State\n  {'-' * 13}\n")
    msg = f"  ERROR: There is no '{file}' file, using default blockdata\n"
    if err == 1:
        print(msg)
    buf = len(max(list(label_dict.values()), key=len)) + 2
    for k, v in label_dict.items():
        if k[1] != "r":
            count = block_count[k] + 1
            list_ = [str(bool(x)) for x in addr[k][1][1:count]]
            print(f"  {v:<{buf}}: ", f"{', '.join(list_)}")
        else:
            count = block_count[k] + 1
            list_ = [str(x) for x in addr[k][1][1:count]]
            print(f"  {v:<{buf}}:", f"[ {', '.join(list_)} ]")
    print()

    # // Start the Modbus Server //
    print(f"  Listening on {local_ip}:{port} for {remote_ip}:*")
    print(f"  Initiating Modbus daemon... ")
    StartTcpServer(context=context, identity=identity, address=(remote_ip, port))


if __name__ == "__main__":
    if euid != 0:
        print("Running with Effective User ID (euid):", euid)
        sudo_switch()
    err, dict_ = get_blockdata()
    run_pymodbus_server(err, dict_)

# // End //
sys.exit()
