# nocpp (No Charge Point Protocol)
Application for targeted pentesting of a charging station. The application tests the OCPP link between the management system and the management system. In addition to various fuzzing attack scenarios, information gathering is also implemented.

This project is based on the Open-Source OCPP implementation in Python by The Mobility House, which you can find [here](https://github.com/mobilityhouse/ocpp).

## :floppy_disk: Charge Point support

Currently OCPP 1.6-J (JSON) is the only supported version.

## :warning: System Requirements

Please make sure you use Python version 3.10 or higher.  
NOCPP requires several Python libraries:
<ul>
  <li>ocpp</li>
  <li>websocket</li>
  <li>socket</li>
  <li>reportlab</li>
  <li>asyncio</li>
  <li>time</li>
  <li>logging</li>
  <li>random</li>
  <li>types</li>
  <li>art</li>
  <li>PyPDF2</li>
  <li>os</li>
  <li>datetime</li>
</ul>

## :white_check_mark: Getting Started

To execute the application, run Main.py.
You can use the following console arguments:
<ul>
  <li>skip-websocket-config (Skips the manual WebSocket setup and uses default values. This argument blocks the set arguments.)</li>
  <li>set-ip-address=[ipv4-address] (Set a specific IPv4 Address, uses default if the specified address is invalid.)</li>
  <li>set-port=[port] (Set a specific port, uses default if the specified port is invalid.)</li>
</ul>
