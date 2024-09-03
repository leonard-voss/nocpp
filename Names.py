# Required libraries
import types

# States for the State Machine, highly-readable format
state_machine = types.SimpleNamespace()
state_machine.INIT = 0
state_machine.INFORMATION_GATHERING = 1
state_machine.ATTACK_SZENARIOS = 2
state_machine.END = 3

#   Variable to generate reports
report_state = types.SimpleNamespace()
report_state.IDLE = 0
report_state.INIT = 1
report_state.CONFIGURATION = 2
report_state.GET_CONFIGURATION = 3
report_state.ATTACKS = 4

# Not sure if we need this feature yet.
error_state = types.SimpleNamespace()
error_state.NO_ERROR = 0
error_state.ALREADY_REPORTED = 1
