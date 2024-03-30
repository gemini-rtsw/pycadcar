from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto

import sys


#try import locally for testing
sys.path.insert(0, '../')
from pygeminirec.applyrecord import ApplyRecord
from pygeminirec.base import CARState
from pygeminirec.base import CADDirective




# State Table
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
#       1         |  START  |     2      |       yes
#       1         |  STOP   |     0      |       yes
# ----------------|---------|------------|-----------------
#       2         |  MARK   |     1      |       yes
#       2         |  CLEAR  |     0      |       yes
#       2         |  PRESET |     2      |       yes
#       2         |  START  |     0      |       yes
#       2         |  STOP   |     0      |       yes
#
#see figure 2 in Gemini Record Reference Manual

# State Machine
class CADStateMachine:
    def __init__(self):
        self.state = 0
        self.funct_ptr = None
        self.parent = None

    async def transition(self, event):
        print(f"CAD state transition and subroutine execution: state: {self.state} event: {event}")


        print("HAWI fix this ret must be clid/val")
        # success by default - if nothing processes SNAM its a success

        ret = 1 
        ret_mess = ''

        if self.state == 0:
            print("state 0")
            if event == CADDirective.MARK:
                print(f"CAD state: {CADDirective.MARK}")
                self.state = 1
                ret, ret_mess = await self.funct_ptr(event)
            elif event == CADDirective.START:
                print(f"CAD state: {CADDirective.START}")
                self.state = 1
                ret, ret_mess = await self.funct_ptr(event)

        elif self.state == 1:
            print("state 1")
            if event == CADDirective.STOP or event == CADDirective.CLEAR:
                print(f"CAD state: {CADDirective.STOP} or {CADDirective.CLEAR}")
                self.state = 0
                ret, ret_mess = await self.funct_ptr(event)
            elif event == CADDirective.START or event == CADDirective.PRESET:
                print(f"CAD state: {CADDirective.START} or {CADDirective.PRESET}")
                self.state = 2
                ret, ret_mess = await self.funct_ptr(event)

        elif self.state == 2:
            print("state 2")
            if event == 'CLEAR' or event == 'START' or event == 'STOP':
                print(f"CAD state: {CADDirective.CLEAR} or {CADDirective.START} or {CADDirective.STOP}")
                self.state = 0
                ret, ret_mess = await self.funct_ptr(event)
            elif event == 'MARK':
                print(f"CAD state: {CADDirective.MARK}")
                self.state = 1
                ret, ret_mess = await self.funct_ptr(event)

        return ret, ret_mess




class CADRecord(ApplyRecord):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_machine = CADStateMachine()
        self.state_machine.parent = self
        self.state_machine.state = 0
        self.state_machine.funct_ptr = self.default_subroutine



# Override these functions to implement CAD actions
# note: they MUST call setSuccess or setError
        
    async def mark(self):
        print("MARK")
        return self.CLID.value, "Directive Processed Successfully"

    async def stop(self):
        print("STOP")
        return self.CLID.value, "Directive Processed Successfully"

    async def clear(self):
        print("CLEAR")
        return self.CLID.value, "Directive Processed Successfully"

    async def preset(self):
        print("PRESET")
        return self.CLID.value, "Directive Processed Successfully"

    async def start(self):
        print("START")
        return self.CLID.value, "Directive Processed Successfully"

    async def default_subroutine(self, event):
            if event == CADDirective.MARK:
                return await self.mark()
            elif event == CADDirective.STOP:
                return await self.stop()
            elif event == CADDirective.CLEAR:
                return await self.clear()
            elif event == CADDirective.PRESET:
                return await self.preset()
            elif event == CADDirective.START:
                return await self.start()



    async def process_directive(self, **kwargs):

        clid = self.CLID.value
        directive = kwargs['directive']

        # IDLE signals we are about to process directive
        print("Set CARs to IDLE")
        await self.update_all_car_states(reverse = True, state = CARState.IDLE, message = f"Processing Directive IDLE {self.prefix}DIR = {directive}", clid = clid)


        # CAD sets it's CAR state to BUSY, which will in turn process any sub CARs
        await self.update_all_car_states(reverse = False, state = CARState.BUSY, message = f"Processing Directive BUSY {self.prefix}DIR = {directive}", clid = clid)

        print(f"Processing CAD Directive {{self.prefix}} with ", kwargs)
        # transition to next state and posibly execute subroutine for state
        ret, ret_mess = await self.state_machine.transition(directive)

        await self.MARK.write(self.state_machine.state)
        print(f'{self.prefix}CAD state is now: {self.state_machine.state}')

        if ret > 0 :
            print(f"Completed Directive with SUCCESS set CAR to {CARState.IDLE} and all CADs to return {ret}")
            await self.set_state(state = ret, message = ret_mess, clid = clid)
            await self.update_all_car_states(reverse = True, state = CARState.IDLE, message = f"Processing Directive IDLE {self.prefix}DIR = {directive}", clid = clid)
        else:
            print(f"Completed Directive with ERROR set CAR to {CARState.ERR} and update failed CAD with error")
            await self.set_state(val = ret, message = ret_mess, clid = clid)
            await self.update_all_car_states(reverse = True, state = CARState.ERR, message = f"Processing Directive IDLE {self.prefix}DIR = {directive}", clid = clid)


        return ret, ret_mess

    # ------------------  DIR -------------------------
    async def DIRputter(self, instance, value):
        print(f'{self.prefix}DIR value changed to: {value}')

        return value

    
    # ------------------  SNAM -------------------------
    SNAM = pvproperty(value=0, dtype=caproto.ChannelType.STRING, name="SNAM")

    async def setSNAM(self, funct_ptr):
        self.state_machine.funct_ptr = funct_ptr
        await self.SNAM.write(funct_ptr.__name__)


    # Other CAD Fields
    OMSS = pvproperty(value='N/A', dtype=caproto.ChannelType.STRING, name="OMSS")
    MARK = pvproperty(value=0, dtype=caproto.ChannelType.INT, name="MARK") #MARK stores the state machine state in a PV


    

    
