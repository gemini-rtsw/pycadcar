from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto

#try import locally for testing
sys.path.insert(0, '../')
from pygeminirec.applyrecord import ApplyRecord
from pygeminirec.applyrecord import CARState


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




class CARRecord(PVGroup):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
#        self.state = CARStateMachine()

#        self.state.state = 'IDLE'

    VAL = pvproperty(
        value=CARState.IDLE,
        dtype=caproto.ChannelType.ENUM,
        enum_strings=[CARState.IDLE, CARState.PAUSED, CARState.BUSY, CARState.ERR],
        name="VAL"
    )
        
#    VAL = pvproperty(
#        value=0,  # Assuming 0 as the default integer value
#        dtype=caproto.ChannelType.LONG,
#        name="VAL"
#    )

    CLID = pvproperty(value=0, dtype=caproto.ChannelType.LONG, name="CLID")

    OMSS = pvproperty(value='N/A', dtype=caproto.ChannelType.STRING, name="OMSS")

    @VAL.startup
    async def VAL(self, instance, async_lib):
        # This function will be called when the IOC starts up.
        print(f'{self.prefix}VAL pvproperty has started.')

    @VAL.putter
    async def VAL(self, instance, value):
        print(f'{self.prefix}VAL value changed to: {value}')
        #self.state.transition(value)
        #print(f'{self.prefix}CAR state is now: {self.state.state}')
        return value
