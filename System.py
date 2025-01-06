import socket
import logging
import CSMS
import asyncio
import random
import websockets

# Required project files
import Report
import Names

# Used to create an unique session and create a individual file name for the report
session_id = ''

# List containing all contents of the test report
# Report document is the list where the finale report is generated from
report_document = []

# This list is used to store the generated table of contents and is added
# to the report document in the final generation process 
template_document = []

# Global variables used by different functions
websocketServer = None
ip_address_websocket_server = None
port_websocket_server = None
protocol_version_websocket_server = None
timeout = False



# Generate a random session token with a specific length
def generateSessionToken(length):
    # Input characters that are allowed for random name generation
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    token = 'nocpp-report-'
    
    for i in range(length):
        token = token + str(random.choice(letters))

    return token



# Initialization function, is called first when the system starts
def init(title, subtitle, software_version):
    print(subtitle + "\nVersion: " + software_version, end='\n\n')
    
    # Generate report template (title page)
    template_document.append(
        Report.build_template(
            title=title, 
            subtitle=subtitle, 
            software_version=software_version
        )
    )

    # Create global session token
    global session_id 
    session_id = generateSessionToken(5)

    print('Test report')
    print(">>\tSession ID: " + str(session_id))

    return Names.error_state.NO_ERROR


# Used for data transfer between files
async def triggerTimeOutError(exception):
    print("TIMEOUT DETECTED:")
    global timeout 
    timeout = True
    print(str(exception))



# Used for data transfer between files
def getTimeOutState():
    global timeout
    return timeout



# Starting the websocket server, which is used to communicate with the charging station via the OCPP protocol.
async def startWebSocketServer():
    print("\n>>\tStarting Websocket Server...\n")

    global websocketServer
    websocketServer = await websockets.serve(
        on_connect, ip_address_websocket_server, port_websocket_server, subprotocols=[protocol_version_websocket_server]
    )

    print("\n>>\tWebsocket  Server started successfully...\n")

    logging.info("Server Started successfully, listening to new connections...")
    await websocketServer.wait_closed()
    

# Forces the web server to shut down, for example if the program terminates due to a timeout.
async def killWebSocketServer():
    print(">>\tTry to shutdown WebSocket Server")
    global websocketServer
    websocketServer.close()
    print("WebSocket Server shutdown complete")



# Used to store the websocket and application configuration to the report document
def store_configuration(system_version, protocol_version, ip_address, port, boot_timestamp):
    #   Add data to job
    job_data = dict()

    job_data['General'] = [
        ['Parameter', 'Value'],
        ['Boot Timestamp', str(boot_timestamp)],
        ['(NOCPP) Software Version', str(system_version)],
        ['(OCPP) Protocol Version (JSON)', str(protocol_version)],
        ['Session Identification Number', str(session_id)]
    ]

    job_data['WebSocket'] = [
        ['Parameter', 'Value'],
        ['(Portal) IPv4 Address', str(ip_address)],
        ['(Portal) Port number', str(port)]
    ]

    # Create report job
    job = create_report_job(title='Configuration', number=Names.report_state.CONFIGURATION, data=job_data)    
    
    # Add generate content to the report document
    report_document.append(
        Report.build_document(job, insertPageBreakAfter=True)
    )


    # Set global variables for data transfer between files and functions
    global ip_address_websocket_server, port_websocket_server, protocol_version_websocket_server

    ip_address_websocket_server = ip_address
    port_websocket_server = port
    protocol_version_websocket_server = protocol_version

    return 0



# Custom data type used for documentation.
def create_report_job(title, number, data):
    job = {
        'title': title,
        'number': number,
        'data': data
    }
    return job



# Used to get the local Ip-Address of the host (CSMS)
def getLocalIpAddress():
    return socket.gethostbyname_ex(socket.gethostname())[-1]



# Used to manually configure the IP address.
def getIpAddress(default_ip):
    # You can change the default IP address in Main.py
    print(">>\tDefault IP Adress is: " + str(default_ip))

    ip = default_ip

    answer = ''

    # Validate user input data
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



# Process to verify that a IPv4 address is valid
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
    


# Function to check if a port is valid
def verify_port_number(port):
    if (int(port) >= 0 and int(port) <= 65535):
        return True
    else:
        return False



# Configurate port used for the websocket connection
def getPort(default_port):
    # You can change the default port in Main.py
    print(">>\tDefault port is: " + str(default_port))

    port = default_port
    answer = ''

    # Verify user input data
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
                    # Warning: This function does not check whether reserved ports are entered
                    # Warning: This function does not check if the ip in combination with this port is valid
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


# Add anything to the report document
def add_to_document(data):
    report_document.append(data)
    return 0


# Finally generate a report document
def generate_report():
    # Add table of contents to the report
    template_document.append(
        Report.build_table_of_contents()
    )
    export_document = template_document + report_document

    # Specify document format and generate the document finally
    filename = str(session_id) + '.pdf'
    Report.render_document(data=export_document, filename=filename)
    print(">>\tDocument rendered successfully")



'''
This function permanently monitors the connection to the charging station.
'''
async def on_connect(websocket, path):

    """
    For every new charge point that connects,
    create a ChargePoint instance and start listening for messages.
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

    # Create ChargePoint object
    cp = CSMS.ChargePoint(charge_point_id, websocket)

    '''
        Because both functions are concurrent and loops, they have to
        be executed as tasks -> comparable to Multi-Threading
    ''' 

    # Task used as a controller (state machine)
    controller_task = asyncio.create_task(
        cp.controller(session_id=session_id, scheduling_pause_time=1)
    )

    # Task to read incoming OCPP messages
    ocpp_messages_task = asyncio.create_task(
        cp.start()
    )

    # Scheduling and Shutdown process
    await controller_task

    print(">>\t Collecting remaining data and shutdown application")
    await asyncio.sleep(10)

    if getTimeOutState() != True:
        # Shutdown websocket server
        await killWebSocketServer()

        ocpp_messages_task.cancel()

        await ocpp_messages_task