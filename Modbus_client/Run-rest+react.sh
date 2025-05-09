#!/bin/bash



#just a bash file to call both rather than doing manually
python3 modbus_webserver.py & 
sleep 1

echo "Starting React frontend..."
cd  modbus-react-client 
npm start >react.log 2>&1 &

echo "starting at http://0.0.0.0: 3000"  

