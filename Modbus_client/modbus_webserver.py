#!/usr/bin/env python3
""" using waitress for production"""

from waitress import serve
import modbus_rest

#It will run in port 8000 and call the mosbus_rest.py
serve(modbus_rest.app, host='0.0.0.0', port=8000)
