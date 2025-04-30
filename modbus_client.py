#!/usr/bin/env python3
""" Modbus Client CLI using ANSI colors """

import argparse
import sys

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

def main():
    args = parse_args()
    print(f"Connecting to {args.ip}:{args.port}")

if __name__ == "__main__":
    main()
