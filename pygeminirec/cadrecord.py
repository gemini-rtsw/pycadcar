from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto

import sys


#try import locally for testing
sys.path.insert(0, '../')
from pygeminirec.applyrecord import ApplyRecord
from pygeminirec.base import BaseExecutor
from pygeminirec.base import CARState
from pygeminirec.base import CADDirective

from pygeminirec.recordlinks import debug_print



# State Table - see figure 2 in Gemini Record Reference Manual
#
#  Current State  |  Event  | Next State |  SNAME and links
# ----------------|---------|------------|-----------------
#       0         |  MARK   |     1      |       yes
#       0         |  CLEAR  |     0      |       yes
#       0         |  PRESET |     0      |       no
#       0         |  START  |     0      |       no
#       0         |  STOP   |     0      |       no
# ----------------|---------|------------|-----------------
#       1         |  MARK   |     1      |       yes
#       1         |  CLEAR  |     0      |       yes
#       1         |  PRESET |     2      |       yes
#       1         |  START  |     0      |       yes   (*) 
#       1         |  STOP   |     0      |       yes
# ----------------|---------|------------|-----------------
#       2         |  MARK   |     1      |       yes
#       2         |  CLEAR  |     0      |       yes
#       2         |  PRESET |     2      |       yes
#       2         |  START  |     0      |       yes
#       2         |  STOP   |     0      |       yes
# 
#
# (*) official docs say:  1 |  START  | 2 | yes 
#     however that state stransition didnt work 
#     with seqexec

# State Machine
class CADStateMachine:
    def __init__(self, cad):
        self.state = 0
        self.cad = cad

        self.result = True
        # Defining the state transition table
        self.transitions = {
            (0, CADDirective.MARK):   (1, self.cad.mark),
            (0, CADDirective.CLEAR):  (0, self.cad.clear),
            (1, CADDirective.MARK):   (1, self.cad.mark),
            (1, CADDirective.CLEAR):  (0, self.cad.clear),
            (1, CADDirective.PRESET): (2, self.cad.preset),
            (1, CADDirective.START):  (0, self.cad.start),
            (1, CADDirective.STOP):   (0, self.cad.stop),
            (2, CADDirective.MARK):   (1, self.cad.mark),
            (2, CADDirective.CLEAR):  (0, self.cad.clear),
            (2, CADDirective.PRESET): (2, self.cad.preset),
            (2, CADDirective.START):  (0, self.cad.start),
            (2, CADDirective.STOP):   (0, self.cad.stop),
            # For no-op events, map to self state with None action
            (0, CADDirective.PRESET): (0, None),
            (0, CADDirective.START):  (0, None),
            (0, CADDirective.STOP):   (0, None),
        }

    async def transition(self, event):
        debug_print("++++++++++++++++++++++++++++++++++++++++++")
        debug_print(f"Executing CAD State Transition from State: {self.state} with Event: {event}")

        # Lookup the event in the transition table
        action_info = self.transitions.get((self.state, event))


        if action_info is not None:
            next_state, action = action_info

            if action:  # If there's an action defined, perform it
                debug_print(f"Action for state {self.state} and event {event}: {action.__self__.__class__.__name__}.{action.__name__}")
                res = await action()
                debug_print("++++++++++++++++++++++++++++++++++++++++++")
                self.result = res
            else:
                debug_print(f"No action for state {self.state} and event {event}.")
                debug_print("++++++++++++++++++++++++++++++++++++++++++")
                self.result = True  # No action needed, but transition is successful

            self.state = next_state  # Transition to the next state
        else:
            debug_print(f"No transition defined for state {self.state} and event {event}.")
            debug_print("++++++++++++++++++++++++++++++++++++++++++")
            self.result = False




class CADRecord(ApplyRecord):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
      #  super().__init__(*args, **kwargs)
        PVGroup.__init__(self, *args, **kwargs)  # Explicitly call PVGroup's constructor
        BaseExecutor.__init__(self)  # Explicitly call BaseExecutor's constructor
    
        self.state_machine = CADStateMachine(self)
        self.state_machine.parent = self
        self.state_machine.state = 0


# Override these functions to implement CAD actions
# note: they MUST call setSuccess or setError
        
    async def mark(self):
        await self.MESS.write("MARK Directive Processed Successfully")
        return True

    async def stop(self):
        await self.MESS.write("STOP Directive Processed Successfully")
        return True

    async def clear(self):
        await self.MESS.write("CLEAR Directive Processed Successfully")
        return True

    async def preset(self):
        await self.MESS.write("PRESET Directive Processed Successfully")
        return True

    async def start(self):
        await self.MESS.write("START Directive Processed Successfully")
        return True


    async def process_cad_directive(self, **kwargs):

        clid = self.CLID.value
        directive = kwargs['directive']

        # IDLE signals we are about to process directive
        debug_print("-----------------------------------")
        debug_print("Set CARs to IDLE")
        await self.update_all_car_states(reverse = True, state = CARState.IDLE, message = f"Processing Directive IDLE {self.prefix}DIR = {directive}", clid = clid)


        # CAD sets it's CAR state to BUSY, which will in turn process any sub CARs
        debug_print("-----------------------------------")
        debug_print("Set CARs to BUSY")
        await self.update_all_car_states(reverse = False, state = CARState.BUSY, message = f"Processing Directive BUSY {self.prefix}DIR = {directive}", clid = clid)


        debug_print("-----------------------------------")
        debug_print(f"Processing CAD Directive {self.prefix} with {kwargs}")
        # transition to next state and posibly execute subroutine for state

        #ret = await self.state_machine.transition(directive)

        await self.DIR.write(directive)
        ret = self.state_machine.result


        await self.MARK.write(self.state_machine.state)
        debug_print(f'{self.prefix}CAD state is now: {self.state_machine.state}')



        if ret is None:
            # Handle the unexpected None case. For example, log an error and set a default error value.
            debug_print("Warning: ret is None, which is unexpected. Defaulting to error state.")
            ret = -1  # Default error value or appropriate handling

        if ret == True :
            #on success CAD.VAL == CAD.CLID
            debug_print("-----------------------------------")
            debug_print("Set CARs to IDLE")
            debug_print(f"Completed Directive with SUCCESS set CAR to {CARState.IDLE} and all CADs to return {clid}")
            await self.VAL.write(clid)
            await self.update_all_car_states(reverse = True, state = CARState.IDLE, message = f"Processing Directive IDLE {self.prefix}DIR = {directive}", clid = clid)
        else:
            #on error CAD.VAL <= 0
            debug_print("-----------------------------------")
            debug_print("Set CARs to ERROR")
            debug_print(f"Completed Directive with ERROR set CAR to {CARState.ERR} and update failed CAD with error")
            await self.VAL.write(ret)
            await self.update_all_car_states(reverse = True, state = CARState.ERR, message = f"{self.MESS.value}", clid = clid)


        return ret 

    # ------------------  DIR -------------------------
    async def DIRputter(self, instance, value):
        debug_print(f'{self.prefix}DIR value changed to: {value}')
        await self.state_machine.transition(value)


    
    # ------------------  SNAM -------------------------
    SNAM = pvproperty(value=0, dtype=caproto.ChannelType.STRING, name="SNAM")

    async def setSNAM(self, funct_ptr):
        self.state_machine.funct_ptr = funct_ptr
        await self.SNAM.write(funct_ptr.__name__)


    # Other CAD Fields
    #OMSS = pvproperty(value='N/A', dtype=caproto.ChannelType.STRING, name="OMSS")
    MARK = pvproperty(value=0, dtype=caproto.ChannelType.INT, name="MARK") #MARK stores the state machine state in a PV


    

    
