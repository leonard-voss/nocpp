# Import Libraries
try:
    # General
    import websockets
    import asyncio
    import logging
    from datetime import datetime
    import sys

    # Application files
    import System

except ModuleNotFoundError:
    print("ERROR: This example relies on several packages. Please make sure you have all required libraries installed.")
    import sys
    sys.exit(1)


# Constants and global variables
TITLE = 'No Charge Point Protocol'
SUBTITLE = 'NOCPP'
SOFTWARE_VERSION = '1.0'
DEFAULT_IP_ADDRESS = '10.8.0.46'
DEFAULT_PORT = 9000
PROTOCOL_VERSION = 'ocpp1.6'
SKIP_WEBSOCKET_CONFIGURATION = True

ip_address = DEFAULT_IP_ADDRESS
port = DEFAULT_PORT
bootTimestamp = datetime.now()

async def main():
    # Start application
    System.init(title=TITLE, subtitle=SUBTITLE, software_version=SOFTWARE_VERSION)

    # Setup Logging
    logging.basicConfig(level=logging.INFO) # If you need more output, change this variable to logging.DEBUG

    # Adjusting the configuration of the WebSocket
    print('\nWebsocket Configuration')

    ip_address = DEFAULT_IP_ADDRESS
    port = DEFAULT_PORT

    if (SKIP_WEBSOCKET_CONFIGURATION != True) and ('skip-websocket-config' not in sys.argv):
        
        ip_console_argument = False
        port_console_argument = False

        for entry in sys.argv:
            if entry.count('set-ip-address=') == 1:
                ip_address = entry.replace('set-ip-address=', '')
                if System.verify_ip_address(ip_address=ip_address) == True:
                    ip_console_argument = True
                    break
                else:
                    print(">>\tConsole argument value for IP address is invalid. Using manual ip configuration instead.")

        if ip_console_argument == False:
            ip_address = System.getIpAddress(DEFAULT_IP_ADDRESS)

        for entry in sys.argv:
            if entry.count('set-port=') == 1:
                port = entry.replace('set-port=', '')
                if System.verify_port_number(port=port) == True:
                    port_console_argument = True
                    break
                else:
                    print(">>\tConsole argument value for port number is invalid. Using manual port configuration instead.")

        if port_console_argument == False:
            port = System.getPort(DEFAULT_PORT)

    else:
        print(">>\tDEBUG-Option: Skip WebSocket Configuration, using Default configuration")


    print(">>\tIP-Address: " + str(ip_address))
    print(">>\tPort number: " + str(port))

    System.store_configuration(SOFTWARE_VERSION, PROTOCOL_VERSION, ip_address, port, bootTimestamp)

    #System.generate_report()

    # Initialization of the OCPP connection
    print('\nOCPP connection and State Machine')

    server = await websockets.serve(
        System.on_connect, ip_address, port, subprotocols=[PROTOCOL_VERSION]
    )

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()

#   Execute main function
asyncio.run(main())
