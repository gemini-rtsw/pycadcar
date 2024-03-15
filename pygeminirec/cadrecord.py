from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto

import sys


#try import locally for testing
sys.path.insert(0, '../')
from pygeminirec.applyrecord import ApplyRecord
from pygeminirec.applyrecord import Result



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

    async def transition(self, event):
        print("CAD state transition and subroutine execution")
        if self.state == 0:
            if event == 'MARK':
                self.state = 1
                await self.funct_ptr(event)
        elif self.state == 1:
            if event == 'STOP' or event == 'CLEAR':
                self.state = 0
                await self.funct_ptr(event)
            elif event == 'START' or event == 'PRESET':
                self.state = 2
                await self.funct_ptr(event)
        elif self.state == 2:
            if event == 'CLEAR' or event == 'START' or event == 'STOP':
                self.state = 0
                await self.funct_ptr(event)
            elif event == 'MARK':
                self.state = 1
                await self.funct_ptr(event)

        return self.state




class CADRecord(ApplyRecord):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = CADStateMachine()
        self.state.state = 0
        self.state.funct_ptr = self.default_subroutine

        self.car_record = None


    async def mark(self):
        print("MARK")
        self.setSuccess("MARK Successful")

    async def stop(self):
        print("STOP")
        self.setSuccess("STOP Successful")

    async def clear(self):
        print("CLEAR")
        self.setSuccess("CLEAR Successful")

    async def preset(self):
        print("PRESET")
        self.setSuccess("PRESET Successful")

    async def start(self):
        print("START")
        self.setSuccess("START Successful")

    async def default_subroutine(self, event):
            if event == 'MARK':
                await self.mark()
            elif event == 'STOP':
                await self.stop()
            elif event == 'CLEAR':
                await self.clear()
            elif event == 'PRESET':
                await self.preset()
            elif event == 'START':
                await self.start()


    # ------------------  DIR -------------------------
    async def DIRputter(self, instance, value):

        print(f'{self.prefix}DIR value changed to: {value}')
        await self.state.transition(value)

        await self.MARK.write(self.state.state)

        print(f'{self.prefix}CAD state is now: {self.state.state}')

        await super().DIRputter(instance, value)

        return value

    # ------------------  VAL  ------------------------- 
    async def VALputter(self, instance, value):
        await super().VALputter(instance, value)

        print(f'{self.prefix}VAL value changed to: {value}')

        if (self.car_record != None):
            await self.car_record.VAL.write(value)

        return value
    

    # ------------------  MESS  ------------------------- 
    async def MESSputter(self, instance, value):
        await super().MESSputter(instance, value)

        print(f'{self.prefix}MESS value changed to: {value}')
        await self.OMSS.write(self.MESS.value)

        if (self.car_record != None):
            await self.car_record.OMSS.write(value)

        return value
    
    # ------------------  SNAM -------------------------
    SNAM = pvproperty(value=0, dtype=caproto.ChannelType.STRING, name="SNAM")

    async def setSNAM(self, funct_ptr):
        self.state.funct_ptr = funct_ptr
        await self.SNAM.write(funct_ptr.__name__)


    # Other CAD Fields
    OMSS = pvproperty(value='N/A', dtype=caproto.ChannelType.STRING, name="OMSS")
    MARK = pvproperty(value=0, dtype=caproto.ChannelType.INT, name="MARK") #MARK stores the state machine state in a PV


    

    
