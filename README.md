# nocpp (No Charge Point Protocol)
## :clipboard: Description
Application for targeted pentesting of a charging station. The application tests the OCPP link between the Charge Point (CP) and the Charge Station Management System (CSMS). In addition to various fuzzing attack scenarios, information gathering is also implemented.

This project is based on the Open-Source OCPP implementation in Python by The Mobility House, which you can find [here](https://github.com/mobilityhouse/ocpp).

## :floppy_disk: Charge Point support

Currently OCPP 1.6-J (JSON) is the only supported version.

## :warning: System Requirements

Please make sure you use Python version 3.10 or higher.  

This application requires a modified version of the ocpp and the websockets libraries.
Both extensions are included in this repository.

NOCPP also requires several additional Python3 libraries:
<ul>
  <li>socket</li>
  <li>reportlab</li>
  <li>asyncio</li>
  <li>logging</li>
  <li>random</li>
  <li>types</li>
  <li>PyPDF2</li>
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

## :bomb: Attack Szenarios

NOCPP uses various attack techniques, including inserting different data types and data values, as well as code injection. Please note that the effectiveness of this tool varies depending on the charging station. NOCPP recognizes successful system requests as well as error messages. In the event of a connection interruption (timeout), this is noted and the program is safely shut down. Due to the asynchronous program structure, this process can take significantly longer than the generation of the result PDF.
