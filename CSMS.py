# Import libraries
from ocpp.routing import on, after
import ocpp.v16
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call
from ocpp.v16.enums import Action, RegistrationStatus
from datetime import datetime
import time
import asyncio
import random
import string
import sys

# Import required system files
import System
import Names
import Report


# If an event has been monitored before, do not add it to the report document again
events_monitored = []

# Global variables used in different attack szenarios
# Only default values, modified by GetConfiguration action
timeout_interval = 30
heartbeat_interval = 10
number_of_connectors = 1

# Class ChargePoint
class ChargePoint(cp):
    # Controller in a state machine to execute attack szenarios
    async def controller(self, session_id, scheduling_pause_time):
        # Initialize the State Machine
        current_state = Names.state_machine.INIT
        timeout_detected = False
        
        # Run State Machine in a infinite loop
        while True:
            # State machine for executing tests

            if (System.getTimeOutState() == True) and (timeout_detected == False):
                timeout_detected = True
                current_state = Names.state_machine.TIMEOUT

            match current_state:
                # Init state -> Currently no function
                case Names.state_machine.INIT:
                    print('\n\n***\tCONTROLLER STATE MACHINE: INIT\t***\n\n')
                    current_state = Names.state_machine.INFORMATION_GATHERING

                # Information Gathering
                case Names.state_machine.INFORMATION_GATHERING:
                    print('\n\n***\tCONTROLLER STATE MACHINE: INFORMATION GATHERING\t***\n\n')
                    await self.getConfiguration()
                    current_state = Names.state_machine.ATTACK_SZENARIOS

                # Attack szenarios
                case Names.state_machine.ATTACK_SZENARIOS:
                    print('\n\n***\tCONTROLLER STATE MACHINE: ATTACK SZENARIOS\t***\n\n')
                    # Wrong Data Type
                    await self.falseDataType()

                    if (System.getTimeOutState() == True):
                        continue
                    
                    # False Data Length
                    await self.falseDataLength()

                    if (System.getTimeOutState() == True):
                        continue

                    # Wrong Data Value (Negative)
                    await self.falseDataNegative()
                    
                    if (System.getTimeOutState() == True):
                        continue

                    # Code Injection, testing if CS Backend can be attacked with Python or Java code
                    await self.codeInjection()
                    
                    # Additional and missing parameters will crash the program -> not included

                    current_state = Names.state_machine.END

                # End state
                case Names.state_machine.END:
                    print('\n\n***\tCONTROLLER STATE MACHINE: END\t***\n\n')
                    #   Generate report document (PDF-File) and exit controller
                    System.generate_report()
                    await asyncio.sleep(5)
                    break

                case Names.state_machine.TIMEOUT:
                    print('\n\n***\tCONTROLLER STATE MACHINE: TIMEOUT\t***\n\n')
                    await System.killWebSocketServer()
                    current_state = Names.state_machine.END
                    
                # Default state -> Used as undefined state case
                case _:
                    print('\n\n***\tCONTROLLER STATE MACHINE: UNDEFINED\t***\n\n')
                    print("[" + str(datetime.datetime.now()) + "]:\t" + "(Controller)\t Undefined state --> Exit")
                    break

            # You need to pause the state machine, because otherwise the
            # listining for ocpp action will not continue correctly
            await asyncio.sleep(scheduling_pause_time)


    # Just for console outputs
    def printEvent(self, eventType):
        print('>>\t' + str(eventType) + " event successfully monitored")


    # Just for console outputs
    def printLine(self):
        print("----------------------------------------")


    '''
        Information Gathering (Fingerprint)
    '''

    # Get Configuration event
    async def getConfiguration(self):
        print("\n>>\tINFORMATION GATHERING: Get Configuration\n\n")

        request = call.GetConfiguration()
        response = await self.call(request)

        job_data = dict()

        data_list = [
            ["Key", "Read only", "Value"]
        ]

        # for each entry
        for entry in response.configuration_key:
            list_entry = []

            list_entry.append(entry['key'])
            list_entry.append(entry['readonly'])
            list_entry.append(entry['value'])

            data_list.append(list_entry)

            # Fetch timeout interval, heatbeat interval and number of connectors of the charge point
            # Store data in global variables
            if entry['key'] == 'ConnectionTimeOut':
                timeout_interval = int(entry['value'])
                print("\n\n>>\tTimout interval fetched: " + str(timeout_interval))

            if entry['key'] == 'HeartbeatInterval':
                heartbeat_interval = int(entry['value'])
                print("\n\n>>\tHeartbeat interval fetched: " + str(heartbeat_interval))

            if entry['key'] == 'NumberOfConnectors':
                number_of_connectors = int(entry['value'])
                print("\n\n>>\tNumber of connectors: " + str(number_of_connectors))
                
        job_data = dict()

        job_data['GetConfiguration'] = data_list
            
        # Generate documentation for this action
        job = System.create_report_job(
            title='Information Gathering', 
            number=Names.report_state.GET_CONFIGURATION, 
            data=job_data
        )
                
        data = Report.build_document(job, insertPageBreakAfter=True)
        System.add_to_document(data)


    async def falseDataType(self):
        # Uses UnlockConnector message
        print("\n>>\tATTACK: False Data Type\t|\tUnlockConnector")

        job_data = dict()

        for i in range(0,3):

            if System.getTimeOutState() == True:
                break


            data_list = [
                ["Parameter", "Value"]
            ]

            data_list.append(['Event', 'UnlockConnector'])

            match(i):
                case 0:
                    # 1. Korrekte Nachricht schicken
                    print("\n\n>>\tFirst attempt: correct data type")
                    action = 'Correct request (Integer)'
                    payload = 1

                case 1:
                    # 2. Manipulierte Nachricht schicken
                    print("\n\n>>\tSecond attempt: wrong data type")
                    action = 'Manipulated request #1 (String)'
                    payload = str(1)

                case 2:
                    # 3. Manipulierte Nachricht schicken
                    print("\n\n>>\tThird attempt: wrong data type")
                    action = 'Manipulated request #2 (Float)'
                    payload = float(1)

            data_list.append(['Payload', payload])
            data_list.append(['Type', type(payload)])

            # Example uses the UnlockConnector call
            request = call.UnlockConnector(payload)
            data_list.append(['Request', str(request)])
            
            try:
                response = await self.call(request)
                data_list.append(['Response (OK)', str(response)])
            except TimeoutError:
                data_list.append(['Response (TIMEOUT)', 'Charge Station connection timed out'])  
            except Exception as error:
                print(error)
                data_list.append(['Response (ERROR)', str(error)])                       
            job_data[action] = data_list
                
        # Generate documentation for this action
        job = System.create_report_job(
            title='Attack: False DataType', 
            number=Names.report_state.ATTACKS, 
            data=job_data
        )
                    
        data = Report.build_document(job, insertPageBreakAfter=True)
        System.add_to_document(data)

        print('\n')        
        self.printLine()

    async def generateRandomString(self):
        length = random.randint(0,1024)
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return random_string

    async def falseDataLength(self):
        print("\n>>\tATTACK: False Data Length\t|\tCancelReservation")
        # Cancel Reservation

        job_data = dict()

        for i in range(0,4):

            if System.getTimeOutState() == True:
                break


            data_list = [
                ["Parameter", "Value"]
            ]

            data_list.append(['Event', 'CancelReservation'])

            match(i):
                case 0:
                    # 1. Korrekte Nachricht schicken
                    print("\n\n>>\tFirst attempt: correct data type")
                    action = 'Correct request'
                    payload = 1

                case 1:
                    # 2. Manipulierte Nachricht schicken
                    print("\n\n>>\tSecond attempt: random String")
                    action = 'Manipulated request #1 (Max Size Integer)'
                    payload = int(sys.maxsize)

                case 2:
                    # 3. Manipulierte Nachricht schicken
                    print("\n\n>>\tThird attempt: random String")
                    action = 'Manipulated request #2 (Random Long String)'
                    payload = await self.generateRandomString()

                case 3:
                    # 4. Manipulierte Nachricht schicken
                    print("\n\n>>\tFourth attempt: empty String")
                    action = 'Manipulated request #3 (Empty String)'
                    payload = '0'

            data_list.append(['Payload', payload])
            data_list.append(['Type', type(payload)])

            # Example uses the UnlockConnector call
            request = call.CancelReservation(payload)
            data_list.append(['Request', str(request)])
            
            try:
                response = await self.call(request)
                data_list.append(['Response (OK)', str(response)])
            except TimeoutError:
                data_list.append(['Response (TIMEOUT)', 'Charge Station connection timed out'])  
            except Exception as error:
                print(error)
                data_list.append(['Response (ERROR)', str(error)])                       
            job_data[action] = data_list
                
        # Generate documentation for this action
        job = System.create_report_job(
            title='Attack: False DataLength', 
            number=Names.report_state.ATTACKS, 
            data=job_data
        )
                    
        data = Report.build_document(job, insertPageBreakAfter=True)
        System.add_to_document(data)

        print('\n')        
        self.printLine()
        

    async def falseDataNegative(self):
        print("\n>>\tATTACK: False Data Value (Negative)\t|\tCancelReservation")
        # ChangeAvailability    

        job_data = dict()

        for i in range(0,2):

            if System.getTimeOutState() == True:
                break


            data_list = [
                ["Parameter", "Value"]
            ]

            data_list.append(['Event', 'CancelReservation'])

            match(i):
                case 0:
                    # 1. Korrekte Nachricht schicken
                    print("\n\n>>\tFirst attempt: correct value")
                    action = 'Correct request'
                    payload = 1

                case 1:
                    # 2. Manipulierte Nachricht schicken
                    print("\n\n>>\tSecond attempt: negative value")
                    action = 'Manipulated request #1 (Negative Integer)'
                    payload = -1


            data_list.append(['Payload', payload])
            data_list.append(['Type', type(payload)])

            # Example uses the UnlockConnector call
            request = call.CancelReservation(payload)
            data_list.append(['Request', str(request)])
            
            try:
                response = await self.call(request)
                data_list.append(['Response (OK)', str(response)])
            except TimeoutError:
                data_list.append(['Response (TIMEOUT)', 'Charge Station connection timed out'])  
            except Exception as error:
                print(error)
                data_list.append(['Response (ERROR)', str(error)])                       
            job_data[action] = data_list
                
        # Generate documentation for this action
        job = System.create_report_job(
            title='Attack: False DataValue', 
            number=Names.report_state.ATTACKS, 
            data=job_data
        )
                    
        data = Report.build_document(job, insertPageBreakAfter=True)
        System.add_to_document(data)

        print('\n')        
        self.printLine()

    async def codeInjection(self):
        # ChangeAvailability    
        print("\n>>\tATTACK: Code Injection / Cross-Site-Scripting\t|\tRemoteStartTransaction")

        job_data = dict()

        for i in range(0,3):

            if System.getTimeOutState() == True:
                break


            data_list = [
                ["Parameter", "Value"]
            ]

            data_list.append(['Event', 'GetDiagnostics'])

            match(i):
                case 0:
                    # 1. Korrekte Nachricht schicken
                    print("\n\n>>\tFirst attempt: Python injection -> OS Detection")
                    action = 'Python code injection (OS detection)'
                    payload = "__import__('os').system('cat /etc/os-release')"

                case 1:
                    # 1. Korrekte Nachricht schicken
                    print("\n\n>>\tSecond attempt: Shell injection -> Delete File System")
                    action = 'Shell injection (Delete File System)'
                    payload = "`; rm -rf /`"

                case 2:
                    # 2. Manipulierte Nachricht schicken
                    print("\n\n>>\tThird attempt: ´Cross-Site-Scripting -> Code Injection")
                    action = 'Cross-Site-Scripting (CSS)'
                    payload = "<script>alert('Cross-Site-Scripting' + ' ' + 'works!'</script>)"


            data_list.append(['Payload', payload])
            data_list.append(['Type', type(payload)])

            # Example uses the UnlockConnector call
            request = call.RemoteStartTransaction(payload)
            data_list.append(['Request', str(request)])
            
            try:
                response = await self.call(request)
                data_list.append(['Response (OK)', str(response)])
            except TimeoutError:
                data_list.append(['Response (TIMEOUT)', 'Charge Station connection timed out'])  
            except Exception as error:
                print(error)
                data_list.append(['Response (ERROR)', str(error)])                       
            job_data[action] = data_list
                
        # Generate documentation for this action
        job = System.create_report_job(
            title='Attack: Code Injection / Cross-Site-Scripting', 
            number=Names.report_state.ATTACKS, 
            data=job_data
        )
                    
        data = Report.build_document(job, insertPageBreakAfter=True)
        System.add_to_document(data)

        print('\n')    
        self.printLine()


    '''
        Actions initiated by the Charge Station (client)
    '''


    # BootNotification, triggered every time the Charge Station boots or reboots
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        if 'BootNotification' not in events_monitored:
            
            print('>>\tBootNotification event successfully monitored')

            job_data = dict()

            # Add required data to job
            job_data['BootNotification'] = [
                ['Parameter', 'Value'],
                ['Charge Point Vendor', str(charge_point_vendor)],
                ['Charge Point Model', str(charge_point_model)],
            ]

            # Add optional data to job
            for key, value in kwargs.items():
                job_data['BootNotification'].append([str(key), str(value)])

            # Generate event documentation
            job = System.create_report_job(
                title='Information Gathering', 
                number=Names.report_state.GET_CONFIGURATION, 
                data=job_data
            )

            data = Report.build_document(data=job, insertPageBreakAfter=False)
                                    
            System.add_to_document(data=data)

            events_monitored.append('BootNotification')
        
        # Required response
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted,
        )


    # StatusNotification, informs the CSMS that the status of the station changed
    @on(Action.StatusNotification)
    def on_status_notification(self, connector_id: int, error_code: str, status:str, vendor_error_code: str, timestamp: str, **kwargs):
        if 'StatusNotification' not in events_monitored:

            print('>>\tStatusNotification event successfully monitored')

            job_data = dict()

            # Add required data to job
            job_data['StatusNotification'] = [
                ['Connector ID', str(connector_id)],
                ['Error Code', str(error_code)],
                ['Status', str(status)],
                ['Vendor Error Code', str(vendor_error_code)],
                ['Timestamp', str(timestamp)]
            ]

            # Add optional data to job
            for key, value in kwargs.items():
                job_data['StatusNotification'].append([str(key), str(value)])

            # Generate event documentation
            job = System.create_report_job(
                title='Information Gathering', 
                number=Names.report_state.GET_CONFIGURATION, 
                data=job_data
            )

            data = Report.build_document(data=job, insertPageBreakAfter=True)

            System.add_to_document(data=data)

            events_monitored.append('StatusNotification')

        # Required event response
        return call_result.StatusNotification()

    # Heartbeat, used for timeout detection and real time clock synchronisation
    @on(Action.Heartbeat)
    async def on_heartbeat(self):
        self.printLine()
        self.printEvent("Heartbeat")
        self.printLine()

        # Required event reponse
        return ocpp.v16.call_result.Heartbeat(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
        )