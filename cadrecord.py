from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto



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
        self.car_record = None
        self.funct_ptr = None

    def transition(self, event):
        if self.state == 0:
            if event == 'MARK':
                self.state = 1
                self.funct_ptr()
        elif self.state == 1:
            if event == 'STOP' or event == 'CLEAR':
                self.state = 0
                self.funct_ptr()
            elif event == 'START' or event == 'PRESET':
                self.state = 2
                self.funct_ptr()
        elif self.state == 2:
            if event == 'CLEAR' or event == 'START' or event == 'STOP':
                self.state = 0
                self.funct_ptr()
            elif event == 'MARK':
                self.state = 1
                self.funct_ptr()

        return self.state




class CADRecord(PVGroup):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = CADStateMachine()

        self.state.state = 0

    async def setSNAM(self, funct_ptr):
        self.state.funct_ptr = funct_ptr
        await self.SNAM.write(funct_ptr.__name__)

    DIR = pvproperty(
        value='MARK',
        dtype=caproto.ChannelType.ENUM,
        enum_strings=['MARK', 'CLEAR', 'PRESET', 'START', 'STOP'],
        name="DIR"
    )

    VAL = pvproperty(
        value='IDLE',
        dtype=caproto.ChannelType.ENUM,
        enum_strings=['IDLE', 'PAUSED', 'BUSY', 'ERROR'],
        name="VAL"
    )

    CLID = pvproperty(value=0, dtype=caproto.ChannelType.LONG, name="CLID")
    OMSS = pvproperty(value='N/A', dtype=caproto.ChannelType.STRING, name="OMSS")

    #MARK stores the state machine state in a PV
    MARK = pvproperty(value=0, dtype=caproto.ChannelType.INT, name="MARK")

    SNAM = pvproperty(value=0, dtype=caproto.ChannelType.STRING, name="SNAM")

    @DIR.startup
    async def DIR(self, instance, async_lib):
        # This function will be called when the IOC starts up.
        print('DIR pvproperty has started.')

    @DIR.putter
    async def DIR(self, instance, value):
        print(f'DIR value changed to: {value}')
        self.state.transition(value)

        await self.MARK.write(self.state.state)

        print(f'CAD state is now: {self.state.state}')
        return value
    
    @VAL.putter
    async def VAL(self, instance, value):
        print(f'VAL value changed to: {value}')
        await self.car_record.VAL.write(value)

        return value
    
