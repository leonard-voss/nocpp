
import socket
import logging
import CSMS
import asyncio
import random
import types

from art import *

import Report
import Names


session_id = ''

# List containing all contents of the test report
report_document = []
template_document = []

# Generate a random session token used to store the report document
def generateSessionToken(length):
    # Input characters that are allowed for random name generation
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    token = 'zcpp-report-'
    
    for i in range(length):
        token = token + str(random.choice(letters))

    return token


# Initialization function, is called first when the system starts
def init(title, subtitle, software_version):
    tprint(title)
    print(subtitle + "\nVersion: " + software_version, end='\n\n')
    
    template_document.append(
        Report.build_template(
            title=title, 
            subtitle=subtitle, 
            software_version=software_version
        )
    )

    global session_id 
    session_id = generateSessionToken(5)

    print('Test report')
    print(">>\tSession ID: " + str(session_id))

    return Names.error_state.NO_ERROR


def store_configuration(system_version, protocol_version, ip_address, port, boot_timestamp):

    #   Add data to job
    job_data = dict()

    job_data['General'] = [
        ['Parameter', 'Value'],
        ['Boot Timestamp', str(boot_timestamp)],
        ['(ZCPP) Software Version', str(system_version)],
        ['(OCPP) Protocol Version (JSON)', str(protocol_version)],
        ['Session Identification Number', str(session_id)]
    ]

    job_data['WebSocket'] = [
        ['Parameter', 'Value'],
        ['(Portal) IPv4 Address', str(ip_address)],
        ['(Portal) Port number', str(port)]
    ]

    #   Execute job and merge files
    job = create_report_job(title='Configuration', number=Names.report_state.CONFIGURATION, data=job_data)    
    
    report_document.append(
        Report.build_document(job, insertPageBreakAfter=True)
    )

    return 0

# Format input data to job
def create_report_job(title, number, data):
    job = {
        'title': title,
        'number': number,
        'data': data
    }

    return job


# Function to get the local Ip-Address of the host (CSMS)
def getLocalIpAddress():
    return socket.gethostbyname_ex(socket.gethostname())[-1]


# Configurate IP address used for WebSocket connection
def getIpAddress(default_ip):
    # You can change the default IP address in Main.py
    print(">>\tDefault IP Adress is: " + str(default_ip))

    ip = default_ip

    answer = ''

    while (answer not in ['Y', 'N']):
        answer = input(">>\tDo you want to change the IP address? (y/n)\n<<\t")
        answer = answer.upper()
        
        match answer:
            # Use individual IP address
            case 'Y':
                print(">>\tChange IP configuration")
                # Print List of local IP addresses
                local_ip_addresses = getLocalIpAddress()
                print(">>\tList of local IP addresses:" + str(local_ip_addresses))

                verify_ip = False

                while verify_ip != True:
                    ip = input(">>\tPlease enter your OCPP portal address (local IPv4 address):\n<<\t")

                    if verify_ip_address(ip_address=ip) == True:
                        verify_ip = True
                    else:
                        print(">>\tInvalid IP address.")

                break

            # Use default ip
            case 'N':
                print(">>\tUsing default IP address")
                break

            # Try again
            case _:
                print(">>\tUndefinded input. Please use only (y/n) for input.")

    print("")
    return ip


def verify_ip_address(ip_address):
    # Check whether the address is valid
    try:
        # Check if number is valid IP
        socket.inet_aton(ip_address)

        # Check IP format (IPv4)
        if ip_address.count('.') > 3 or ip_address.count('.') < 3:
            print(">>\tUndefinded input. Please use only (y/n) for input.")
            return False
        else:
            return True
    except socket.error:
        # Try again
        return False
    
def verify_port_number(port):
    if (int(port) >= 0 and int(port) <= 65535):
        return True
    else:
        return False



# Configurate IP address used for WebSocket connection
def getPort(default_port):
    # You can change the default port in Main.py
    print(">>\tDefault port is: " + str(default_port))

    port = default_port

    answer = ''

    while (answer not in ['Y', 'N']):
        answer = input(">>\tDo you want to change the port? (y/n)\n<<\t")
        answer = answer.upper()
            
        match answer:
            # Use individual port number
            case 'Y':
                print(">>\tChange port configuration")
                # Enter Port number
                verify_port = False

                while verify_port != True:
                    
                    # Ensure input is a number 
                    try:
                        port = int(input(">>\tPlease enter your OCPP portal port:\n<<\t"))
                    except Exception:
                        print(">>\tInvalid port number")
                        continue

                    # Validate that input is a port number
                    # Attention: This function does not check whether reserved ports are entered
                    
                    if verify_port_number(port=port) == True:
                        verify_port = True
                    else:
                        print(">>\tInvalid port number")
                        
                break

            # Use default port
            case 'N':
                print(">>\tUsing default port")
                break

            # Try again
            case _:
                print(">>\tUndefinded input. Please use only (y/n) for input.")

    print("")
    return port


def add_to_document(data):
    report_document.append(data)
    return 0


# Finally generate a report document
def generate_report():

    template_document.append(
        Report.build_table_of_contents()
    )

    export_document = template_document + report_document

    filename = str(session_id) + '.pdf'
    Report.render_document(data=export_document, filename=filename)


# This function permanently monitors the connection to the charging station
async def on_connect(websocket, path):

    """For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError:
        logging.error("Client hasn't requested any Subprotocol. Closing Connection")
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports  %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        return await websocket.close()

    charge_point_id = path.strip("/")
    cp = CSMS.ChargePoint(charge_point_id, websocket)

    '''
        Because both functions are concurrent and loops, they have to
        be executed as tasks -> comparable to Multi-Threading
    ''' 

    # Task used as a controller (state machine) for the tests and documentation
    controller_task = asyncio.create_task(
        #cp.controller(session_id=session_id, scheduling_pause_time=0.001)
        cp.controller(session_id=session_id, scheduling_pause_time=1)
    )

    # Task to read incoming OCPP messages
    start_task = asyncio.create_task(
        cp.start()
    )

    await controller_task
    await start_task
