from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto

import sys


#try import locally for testing
sys.path.insert(0, '../')
from pygeminirec.applyrecord import ApplyRecord
from pygeminirec.base import BaseExecutor
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
        self.result = True

    async def transition(self, event):
        print(f"CAD state transition and subroutine execution: state: {self.state} event: {event}")


        # success by default - if nothing processes SNAM its a success

        self.ret = True


        print("++++++++++++++++++++++++++++++++++++++++++")
        print(f"Executing CAD State Transition from State: {self.state} with Event: {event}")

        if self.state == 0:
            if event == CADDirective.MARK:
                self.state = 1
                self.result = await self.funct_ptr(event)

        elif self.state == 1:
            if event == CADDirective.STOP or event == CADDirective.CLEAR:
                self.state = 0
                self.result  = await self.funct_ptr(event)
            elif event == CADDirective.START or event == CADDirective.PRESET:
                self.state = 2
                self.result = await self.funct_ptr(event)

        elif self.state == 2:
            if event == CADDirective.CLEAR or event == CADDirective.START or event == CADDirective.STOP:
                self.state = 0
                self.result = await self.funct_ptr(event)
            elif event == CADDirective.MARK:
                self.state = 1
                self.result = await self.funct_ptr(event)

        print("++++++++++++++++++++++++++++++++++++++++++")



class CADRecord(ApplyRecord):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
      #  super().__init__(*args, **kwargs)
        PVGroup.__init__(self, *args, **kwargs)  # Explicitly call PVGroup's constructor
        BaseExecutor.__init__(self)  # Explicitly call BaseExecutor's constructor
    
        self.state_machine = CADStateMachine()
        self.state_machine.parent = self
        self.state_machine.state = 0
        self.state_machine.funct_ptr = self.default_subroutine



# Override these functions to implement CAD actions
# note: they MUST call setSuccess or setError
        
    async def mark(self):
        print("MARK")
        await self.MESS.write("Directive Processed Successfully")
        return True

    async def stop(self):
        await self.MESS.write("Directive Processed Successfully")
        return True

    async def clear(self):
        await self.MESS.write("Directive Processed Successfully")
        return True

    async def preset(self):
        await self.MESS.write("Directive Processed Successfully")
        return True

    async def start(self):
        await self.MESS.write("Directive Processed Successfully")
        return True


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



    async def process_cad_directive(self, **kwargs):

        clid = self.CLID.value
        directive = kwargs['directive']

        # IDLE signals we are about to process directive
        print("-----------------------------------")
        print("Set CARs to IDLE")
        await self.update_all_car_states(reverse = True, state = CARState.IDLE, message = f"Processing Directive IDLE {self.prefix}DIR = {directive}", clid = clid)


        # CAD sets it's CAR state to BUSY, which will in turn process any sub CARs
        print("-----------------------------------")
        print("Set CARs to BUSY")
        await self.update_all_car_states(reverse = False, state = CARState.BUSY, message = f"Processing Directive BUSY {self.prefix}DIR = {directive}", clid = clid)


        print("-----------------------------------")
        print(f"Processing CAD Directive {self.prefix} with {kwargs}")
        # transition to next state and posibly execute subroutine for state

        ret = await self.state_machine.transition(directive)

        #await self.DIR.write(directive)
        #ret = self.state_machine.result


        await self.MARK.write(self.state_machine.state)
        print(f'{self.prefix}CAD state is now: {self.state_machine.state}')

        if ret == True :
            #on success CAD.VAL == CAD.CLID
            print("-----------------------------------")
            print("Set CARs to IDLE")
            print(f"Completed Directive with SUCCESS set CAR to {CARState.IDLE} and all CADs to return {clid}")
            await self.VAL.write(clid)
            await self.update_all_car_states(reverse = True, state = CARState.IDLE, message = f"Processing Directive IDLE {self.prefix}DIR = {directive}", clid = clid)
        else:
            #on error CAD.VAL <= 0
            print("-----------------------------------")
            print("Set CARs to ERROR")
            print(f"Completed Directive with ERROR set CAR to {CARState.ERR} and update failed CAD with error")
            await self.VAL.write(ret)
            await self.update_all_car_states(reverse = True, state = CARState.ERR, message = f"Processing Directive IDLE {self.prefix}DIR = {directive}", clid = clid)


        return ret 

    # ------------------  DIR -------------------------
    async def DIRputter(self, instance, value):
        print(f'{self.prefix}DIR value changed to: {value}')
        #await self.state_machine.transition(value)


    
    # ------------------  SNAM -------------------------
    SNAM = pvproperty(value=0, dtype=caproto.ChannelType.STRING, name="SNAM")

    async def setSNAM(self, funct_ptr):
        self.state_machine.funct_ptr = funct_ptr
        await self.SNAM.write(funct_ptr.__name__)


    # Other CAD Fields
    #OMSS = pvproperty(value='N/A', dtype=caproto.ChannelType.STRING, name="OMSS")
    MARK = pvproperty(value=0, dtype=caproto.ChannelType.INT, name="MARK") #MARK stores the state machine state in a PV


    

    
