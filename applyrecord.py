from caproto.server import pvproperty, PVGroup
import caproto


class applyRecord(PVGroup):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    DIR = pvproperty(
        value='MARK',
        dtype=caproto.ChannelType.ENUM,
        enum_strings=['MARK', 'CLEAR', 'PRESET', 'START', 'STOP'],
        name="DIR"
    )
    VAL = pvproperty(value=0, dtype=caproto.ChannelType.LONG, name="VAL")

    MESS = pvproperty(value='N/A', dtype=caproto.ChannelType.STRING, name="MESS")