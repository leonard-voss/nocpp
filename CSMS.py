
from ocpp.routing import on, after
import ocpp.v16
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call
from ocpp.v16.enums import Action, RegistrationStatus
from datetime import datetime

import time
import System
import Names
import asyncio

import Report

events_monitored = []

# Only default values
timeout_interval = 30
heartbeat_interval = 10
number_of_connectors = 1

# Class ChargePoint
class ChargePoint(cp):

    # Controller in a state machine to execute stuff
    async def controller(self, session_id, scheduling_pause_time):
        # Initialize the State Machine
        current_state = Names.state_machine.INIT
        
        # Run State Machine in a infinite loop
        while True:
            # State machine for executing tests
            match current_state:

                case Names.state_machine.INIT:
                    #   Init has currently no function
                    current_state = Names.state_machine.INFORMATION_GATHERING

                case Names.state_machine.INFORMATION_GATHERING:
                    await self.getConfiguration()
                    current_state = Names.state_machine.END

                case Names.state_machine.ATTACK_SZENARIOS:

                    current_state = Names.state_machine.END

                case Names.state_machine.END:
                    #   Generate report document (PDF-File) and exit controller
                    System.generate_report()
                    break

                # Default case
                case _:
                    print("[" + str(datetime.datetime.now()) + "]:\t" + "(Controller)\t Undefined state --> Exit")
                    break

            await asyncio.sleep(scheduling_pause_time)


    def printEvent(self, eventType):
        print(eventType + " event")


    def printLine(self):
        print("----------------------------------------")

    async def getConfiguration(self):
        print(">> Try to get Configuration")

        request = call.GetConfiguration()
        response = await self.call(request)

        self.printLine()

        job_data = dict()

        data_list = [
            ["Key", "Read only", "Value"]
        ]

        # Für jeden Eintrag
        for entry in response.configuration_key:
            list_entry = []

            list_entry.append(entry['key'])
            list_entry.append(entry['readonly'])
            list_entry.append(entry['value'])

            data_list.append(list_entry)

            #   Fetch timeout interval, heatbeat interval and number of connectors of the charge point
            if entry['key'] == 'ConnectionTimeOut':
                timeout_interval = int(entry['value'])
                print(">>\tTimout interval fetched: " + str(timeout_interval))

            if entry['key'] == 'HeartbeatInterval':
                heartbeat_interval = int(entry['value'])
                print(">>\tHeartbeat interval fetched: " + str(heartbeat_interval))

            if entry['key'] == 'NumberOfConnectors':
                number_of_connectors = int(entry['value'])
                print(">>\tNumber of connectors: " + str(number_of_connectors))
                
        job_data = dict()

        job_data['GetConfiguration'] = data_list
            
        
        job = System.create_report_job(
            title='Information Gathering', 
            number=Names.report_state.GET_CONFIGURATION, 
            data=job_data
        )
        
        print('>>\t' + "Get Configuration" + " event successfully monitored")
        
        data = Report.build_document(job, insertPageBreakAfter=True)

        System.add_to_document(data)


    # BootNotification
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        if 'BootNotification' not in events_monitored:
            
            print('>>\tBootNotification event successfully monitored')

            job_data = dict()

            # Hinzufügen der notwendigen Parameter
            job_data['BootNotification'] = [
                ['Parameter', 'Value'],
                ['Charge Point Vendor', str(charge_point_vendor)],
                ['Charge Point Model', str(charge_point_model)],
            ]

            # Hinzufügen der optionalen Parameter
            for key, value in kwargs.items():
                job_data['BootNotification'].append([str(key), str(value)])


            job = System.create_report_job(
                title='Information Gathering', 
                number=Names.report_state.GET_CONFIGURATION, 
                data=job_data
            )

            data = Report.build_document(data=job, insertPageBreakAfter=False)
                                    
            System.add_to_document(data=data)

            events_monitored.append('BootNotification')
        
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted,
        )


    # StatusNotification
    @on(Action.StatusNotification)
    def on_status_notification(self, connector_id: int, error_code: str, status:str, vendor_error_code: str, timestamp: str, **kwargs):
        if 'StatusNotification' not in events_monitored:

            print('>>\tStatusNotification event successfully monitored')

            job_data = dict()

            # Hinzufügen der notwendigen Parameter
            job_data['StatusNotification'] = [
                ['Connector ID', str(connector_id)],
                ['Error Code', str(error_code)],
                ['Status', str(status)],
                ['Vendor Error Code', str(vendor_error_code)],
                ['Timestamp', str(timestamp)]
            ]

            # Hinzufügen der optionalen Parameter
            for key, value in kwargs.items():
                job_data['StatusNotification'].append([str(key), str(value)])

            job = System.create_report_job(
                title='Information Gathering', 
                number=Names.report_state.GET_CONFIGURATION, 
                data=job_data
            )

            data = Report.build_document(data=job, insertPageBreakAfter=True)

            System.add_to_document(data=data)

            events_monitored.append('StatusNotification')

        return call_result.StatusNotification()

    # Heartbeat
    @on(Action.Heartbeat)
    async def on_heartbeat(self):
        self.printLine()
        self.printEvent("Heartbeat")
        self.printLine()
        return ocpp.v16.call_result.Heartbeat(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
        )