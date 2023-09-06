from caproto.server import pvproperty, PVGroup
import caproto



class ApplyRecord(PVGroup):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cad_records = []

    DIR = pvproperty(
        value='MARK',
        dtype=caproto.ChannelType.ENUM,
        enum_strings=['MARK', 'CLEAR', 'PRESET', 'START', 'STOP'],
        name="DIR"
    )

    @DIR.putter
    async def DIR(self, instance, value):
        #Writing the START directive forces the PRESET directive to be sent to all links before the START directive is sent.
        if value == 'START':
            await self.set_cad_dir('PRESET ')

        await self.set_cad_dir(value)
        return value

    VAL = pvproperty(value=0, dtype=caproto.ChannelType.LONG, name="VAL")

    MESS = pvproperty(value='N/A', dtype=caproto.ChannelType.STRING, name="MESS")

    async def set_cad_dir(self, value):
        """Set the DIR value for all cadRecord instances to match applyRecord's DIR."""
        for cad_record in self.cad_records:
            print(f'{cad_record.prefix} Processing ...')
            
            await cad_record.DIR.write(value)

            data = cad_record.VAL.value

            print(f'{cad_record.prefix} CAD VAL: {str(data)}')

            if data == 'ERROR':
                print("Error processing cad record: ", cad_record.prefix)
                await self.VAL.write(1)
                await self.MESS.write(cad_record.MESS.value)
                break

            # ADD PROPER PROCESSING 
            # Check cad VAL for error
            # write error to MESS
            # stop processing







