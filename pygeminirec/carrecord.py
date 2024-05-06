from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto
import sys

#try import locally for testing
sys.path.insert(0, '../')
from pygeminirec.applyrecord import ApplyRecord
from pygeminirec.base import BaseExecutor
from pygeminirec.base import CARState

from pygeminirec.recordlinks import debug_print

# State Table
#
#  Current State  |  Event       | Next State
# ----------------|--------------|------------
#  Unavailable    |  Idle        |    Idle
# ----------------|--------------|------------
#      Idle       |  Busy        |    Busy
#      Idle       |  Unavailable |    Unavailable
# ----------------|--------------|------------
#      Busy       |  Idle        |    Idle
#      Busy       | Paused       |  Paused
# ----------------|--------------|------------
#     Paused      |  Busy        |    Busy
#     Paused      |  Idle        |    Idle
#     Paused      |  Error       |   Error
# ----------------|--------------|------------
#     Error       |  Busy        |    Busy
#     Error       |  Idle        |    Idle
#
#
#see figure 4 in Gemini Record Reference Manual

# State Machine
"""
State machine not implemented. The documentation doesn't match the 
GNIRS implementation. For example there is not UAVAILABLE. Adding it 
causes Enum mismatch. The requirements of Seqexec are simple enough that
the state machine is not needed. States are handled manually.

class CARStateMachine:
    def __init__(self):
        self.state = 'UNAVAILABLE'

    def transition(self, event):
        if self.state == 'UNAVAILABLE':
            if event == IDLE':
                self.state = 'IDLE'
        elif self.state == 'IDLE':
            if event == 'BUSY':
                self.state = 'BUSY'
            elif event == 'UNAVAILABLE':
                self.state = 'UNAVAILABLE'
        elif self.state == 'BUSY':
            if event == 'IDLE':
                self.state = 'IDLE'
            elif event == 'PAUSED':
                self.state = 'PAUSED'
        elif self.state == 'PAUSED':
            if event == 'BUSY':
                self.state = 'BUSY'
            elif event == 'IDLE':
                self.state = 'IDLE'
            elif event == 'ERROR':
                self.state = 'ERROR'
        elif self.state == 'ERROR':
            if event == 'BUSY':
                self.state = 'BUSY'
            elif event == 'IDLE':
                self.state = 'IDLE'

        return self.state
"""




class CARRecord(PVGroup, BaseExecutor):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        PVGroup.__init__(self, *args, **kwargs)  # Explicitly call PVGroup's constructor
        BaseExecutor.__init__(self)  # Explicitly call BaseExecutor's constructor

#        self.car_records = RecordLinks()

#        self.state = CARStateMachine()

#        self.state.state = 'IDLE'
        
    
    async def set_state(self, **kwargs):
        # state - CARState
        # message
        # clid
        debug_print(f'Updating Sub {self.prefix} VAL={kwargs["state"]} CLID={kwargs["clid"]} OMSS={kwargs["message"]}')
        await self.CLID.write(kwargs['clid'])
        await self.OMSS.write(kwargs['message'])
        await self.VAL.write(kwargs['state'])

        return self.CLID.value
    

    async def is_idle(self, **kwargs):

        if (self.VAL.value == CARState.IDLE):
            return True
        
        return False


    VAL = pvproperty(
        value=CARState.IDLE,
        dtype=caproto.ChannelType.ENUM,
        enum_strings=[CARState.IDLE, CARState.PAUSED, CARState.BUSY, CARState.ERR],
        name="VAL"
    )
        

    CLID = pvproperty(value=0, dtype=caproto.ChannelType.LONG, name="CLID")
    @CLID.putter
    async def CLID(self, instance, value):
        await self.CLIDputter(instance, value)

    async def CLIDputter(self, instance, value):
        debug_print(f'{self.prefix}CLID value changed to: {value}')



    OMSS = pvproperty(value='N/A', dtype=caproto.ChannelType.STRING, name="OMSS")

    @VAL.startup
    async def VAL(self, instance, async_lib):
        # This function will be called when the IOC starts up.
        debug_print(f'{self.prefix}VAL pvproperty has started.')

    @VAL.putter
    async def VAL(self, instance, value):
        debug_print(f'{self.prefix}VAL value changed to: {value}')

        return value
