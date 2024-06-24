# Import Libraries
try:
    # General
    import websockets
    import asyncio
    import logging
    from datetime import datetime

    # Application files
    import System

except ModuleNotFoundError:
    print("ERROR: This example relies on several packages. Please make sure you have all required libraries installed.")
    import sys
    sys.exit(1)


# Constants and global variables
TITLE = 'Zero Charge Point Protocol'
SUBTITLE = 'ZCPP'
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
    System.printTitle('WebSocket configuration')

    ip_address = DEFAULT_IP_ADDRESS
    port = DEFAULT_PORT

    if SKIP_WEBSOCKET_CONFIGURATION != True:
        ip_address = System.getIpAddress(DEFAULT_IP_ADDRESS)
        port = System.getPort(DEFAULT_PORT)
    else:
        print(">>\tDEBUG-Option: Skip WebSocket Configuration, using Default configuration")

    System.store_configuration(SOFTWARE_VERSION, PROTOCOL_VERSION, ip_address, port, bootTimestamp)

    System.generate_report()

    # Initialization of the OCPP connection
    System.printTitle('OCPP connection and State Machine')

    server = await websockets.serve(
        System.on_connect, ip_address, port, subprotocols=[PROTOCOL_VERSION]
    )

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()


#   Execute main function
asyncio.run(main())
