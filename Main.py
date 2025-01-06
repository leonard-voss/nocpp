
# Check if the most important libraries and project files for this project are present.
try:
    # General required libraries
    import asyncio
    import logging
    from datetime import datetime
    import sys
    import ocpp
    import websockets

    #Necessary project files
    import System

except ModuleNotFoundError:
    # Exit application if some library or file is missing
    print("ERROR: This example relies on several packages. Please make sure you have all required libraries installed.")
    import sys
    sys.exit(1)


'''
Constants and global variables
'''

# General application settings
TITLE = 'No Charge Point Protocol'
SUBTITLE = 'NOCPP'
SOFTWARE_VERSION = '1.0'

# Default websocket configuration
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
    # Generate template for documentation
    System.init(title=TITLE, subtitle=SUBTITLE, software_version=SOFTWARE_VERSION)

    # Setup Logging
    '''
    Setup OCPP console logging,
    change this variable to logging.DEBUG if you need more output information
    '''
    logging.basicConfig(level=logging.INFO)

    '''
        Websocket configuration, this is the general process description and hierarchy for ip and port selection:

        1.  If console argument skip-websocket-config -> use default values
        
        2.  If console argument set-(ip-address or port)=[ip-address or port] is set, use this value for wesocket configuration. 
            If the value is not valid, use automatically default values instead.
        
        3.  Else, ask user to select ip and port manually.
    '''

    print('\nWebsocket Configuration')

    # Websocket configuration
    if (SKIP_WEBSOCKET_CONFIGURATION != True) and ('skip-websocket-config' not in sys.argv):
        
        # Initialization
        ip_console_argument = False
        port_console_argument = False


         # IP Address configuration
        for entry in sys.argv:
            if entry.count('set-ip-address=') == 1:
                ip_address = entry.replace('set-ip-address=', '')
                # Verify values used by console argument
                if System.verify_ip_address(ip_address=ip_address) == True:
                    ip_console_argument = True
                    break
                else:
                    print(">>\tConsole argument value for IP address is invalid. Using manual ip configuration instead.")

        if ip_console_argument == False:
            ip_address = System.getIpAddress(DEFAULT_IP_ADDRESS)


        # Websocket port configuration
        for entry in sys.argv:
            if entry.count('set-port=') == 1:
                port = entry.replace('set-port=', '')
                # Verify values used by console argument
                if System.verify_port_number(port=port) == True:
                    port_console_argument = True
                    break
                else:
                    print(">>\tConsole argument value for port number is invalid. Using manual port configuration instead.")
        
        if port_console_argument == False:
            port = System.getPort(DEFAULT_PORT)

    else:
        # Skip the websocket configuration and use the predefined values
        print(">>\tDEBUG-Option: Skip WebSocket Configuration, using Default configuration")


    print(">>\tIP-Address: " + str(ip_address))
    print(">>\tPort number: " + str(port))

    # Final documentation of the websocket configuration used
    System.store_configuration(SOFTWARE_VERSION, PROTOCOL_VERSION, ip_address, port, bootTimestamp)

    # This asynchronous call is only executed when the program ends
    await System.startWebSocketServer()

    print('\nFinished Programm execution. You can close this window now.')

    # Infinite loop at the end of the program, user can close program
    while True:
        pass

# Execute main function
asyncio.run(main())