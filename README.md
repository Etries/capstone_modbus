# Capstone Project- Modbus Simulation
## Client-Server Modbus Simulation

A Python-based Modbus server-client-based simulation to inspect and understand the Modbus TCP-based industrial communication. A full-stack is implemented to store and view the status of the simulated control unit.

It is composed of:

- Custom Modbus TCP server initialised via YAML
- Multiple Python-based clients (CLI, GUI, and REST API)
- A React.js frontend for web access to the RESTful A
- Centralised SQLite logging of Modbus

Project Structure:
capstone_modbus/
├── modbus_server/               # Modbus TCP Server
│   ├── blockdata_init.yaml      # Register values (preload config)
│   └── modbus_server.py         # Server implementation
│
├── modbus_client/               # Main client-side directory
│   ├── modbus_client.py         # CLI-based Modbus client
│   ├── gui_client.py            # GUI alternative for modbus_client
│   ├── modbus_rest.py           # REST API using Flask
│   ├── modbus_webserver.py      # Optional alternative API setup
│   ├── modbus_db.sqlite         # SQLite DB (auto-created)
│   ├── modbus-react-client/     # React frontend (Node.js app)
│   ├── Run-rest+react.sh        # Bash script: start REST + React
│   ├── Stop-rest+react.sh       # Bash script: stop REST + React
│            
│   
│
├── requirements.txt             # Python dependencies to install
└── README.md      




## Requirements

Core Technologies
- [Python] >= 3.10 - Used for Modbus Client/Server, RestAPI, and GUI 
- [Nodejs] >= 18 - runnig js as a backend
- [ReactJs] - Frontend javascrip fraework for user-interface.
- [Tailwind CSS] - CSS framework and styling
- [SQLite] - Data Storage

Important Python libraries (included in requirements)
- [Pymodbus] == 3.15 - library for modbus TCP cimmunication
- [Flask] - Lightweight web application framework
- [Flask-RESTful] - Flask extenstion for RESFUL API
- [SQLite3] - lightwieght Local storage or storage of modbus values



## Installation

create vene and Istall requirements
```sh
cd capstone_modbus
python3 -m venv .pymod
source .venv/bin/activate
pip install -r requirements.txt
```

Start the server.

```sh
cd modbus_server
./modbus_server
```

Run client 
```sh
cd modbus_client
./modbus_client.py
```

Run GUI client 
```sh
./gui_client.py
```

Run Web server
```sh
./modbus_webserver.py
```
Run ReactJS
```sh
cd dbus-react-client/ 
.npm start
```





```sh
127.0.0.1:8000
```

## License

SETU


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
