#!/bin/bash

#just a bash file to call both rather than doing manually

pkill -f modbus_webserver.py
sleep 1

cd  modbus-react-client 
npm stop