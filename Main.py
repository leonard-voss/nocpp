# Libraries
try:
    # General required libraries
    import asyncio
    import logging
    from datetime import datetime
    import sys

    # Files required by the application
    import System

except ModuleNotFoundError:
    # Exit application if some library or file is missing
    print("ERROR: This example relies on several packages. Please make sure you have all required libraries installed.")
    import sys
    sys.exit(1)

'''
Constants and global variables
'''

# Application settings
TITLE = 'No Charge Point Protocol'
SUBTITLE = 'NOCPP'
SOFTWARE_VERSION = '1.0'

# Default values
DEFAULT_IP_ADDRESS = '10.8.0.46'
DEFAULT_PORT = 9002
PROTOCOL_VERSION = 'ocpp1.6'
SKIP_WEBSOCKET_CONFIGURATION = True

# Initialize default values
ip_address = DEFAULT_IP_ADDRESS
port = DEFAULT_PORT

# Fetch boot timestamp
bootTimestamp = datetime.now()

async def main():
    # Start application (document to console and generate template)
    System.init(title=TITLE, subtitle=SUBTITLE, software_version=SOFTWARE_VERSION)

    # Setup Logging
    logging.basicConfig(level=logging.INFO) # If you need more output, change this variable to logging.DEBUG

    # Adjusting the configuration of the WebSocket
    print('\nWebsocket Configuration')

    ip_address = DEFAULT_IP_ADDRESS
    port = DEFAULT_PORT

    # WebSocket configuration

    '''
        General process description and hierarchy for ip and port selection:

        1.  If console argument skip-websocket-config -> use default values
        2.  If console argument set-(ip-address or port)=[ip-address or port] 
            is set, use this value for wesocket configuration. If the value is
            not valid, use automatically default values instead.
        3.  Else, ask user to select ip and port manually.
    '''

    # IP Address configuration
    if (SKIP_WEBSOCKET_CONFIGURATION != True) and ('skip-websocket-config' not in sys.argv):
        
        ip_console_argument = False
        port_console_argument = False

        for entry in sys.argv:
            # Detect console argument
            if entry.count('set-ip-address=') == 1:
                ip_address = entry.replace('set-ip-address=', '')
                # Verify values used by console argument
                if System.verify_ip_address(ip_address=ip_address) == True:
                    ip_console_argument = True
                    break
                else:
                    print(">>\tConsole argument value for IP address is invalid. Using manual ip configuration instead.")

        # Manual selection process
        if ip_console_argument == False:
            ip_address = System.getIpAddress(DEFAULT_IP_ADDRESS)

        for entry in sys.argv:
            # Detect console argument
            if entry.count('set-port=') == 1:
                port = entry.replace('set-port=', '')
                # Verify values used by console argument
                if System.verify_port_number(port=port) == True:
                    port_console_argument = True
                    break
                else:
                    print(">>\tConsole argument value for port number is invalid. Using manual port configuration instead.")
        
        # Manual selection process
        if port_console_argument == False:
            port = System.getPort(DEFAULT_PORT)

    else:
        # Constant / setting used in Main.py
        print(">>\tDEBUG-Option: Skip WebSocket Configuration, using Default configuration")


    print(">>\tIP-Address: " + str(ip_address))
    print(">>\tPort number: " + str(port))

    # Store the final WebSocket configuration into the report document
    System.store_configuration(SOFTWARE_VERSION, PROTOCOL_VERSION, ip_address, port, bootTimestamp)

    await System.startWebSocketServer()

    print('\nFinished Programm execution. You can close this window now.')

    while True:
        pass

# Execute main function
asyncio.run(main())