from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto


class cadRecord(PVGroup):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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

    @DIR.startup
    async def DIR(self, instance, async_lib):
        # This function will be called when the IOC starts up.
        print('DIR pvproperty has started.')

    @DIR.putter
    async def DIR(self, instance, value):
        print(f'DIR value changed to: {value}')
        return value