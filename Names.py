
'''
This file defines data types to increase the readability of the code.
'''

import types

# States for the state machine, which controls the sequential execution of the attacks.
state_machine = types.SimpleNamespace()
state_machine.INIT = 0
state_machine.INFORMATION_GATHERING = 1
state_machine.ATTACK_SZENARIOS = 2
state_machine.END = 3
state_machine.TIMEOUT = 4

# States for generating the PDF documentation.
report_state = types.SimpleNamespace()
report_state.IDLE = 0
report_state.INIT = 1
report_state.CONFIGURATION = 2
report_state.GET_CONFIGURATION = 3
report_state.ATTACKS = 4