from caproto.server import pvproperty, PVGroup
import caproto



class ApplyRecord(PVGroup):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_records = []


    # ------------------ DIR  ------------------------- 
    DIR = pvproperty(
        value='MARK',
        dtype=caproto.ChannelType.ENUM,
        enum_strings=['MARK', 'CLEAR', 'PRESET', 'START', 'STOP'],
        name="DIR"
    )

    @DIR.putter
    async def DIR(self, instance, value):
        await self.DIRputter(instance, value)

    async def DIRputter(self, instance, value):
        print(f"{self.prefix} Processing Sub Records: {[obj.__class__.__name__ for obj in self.sub_records]}")
        #Writing the START directive forces the PRESET directive to be sent to all links before the START directive is sent.
        if value == 'START':
            await self.setSubRecordDir('PRESET')

        await self.setSubRecordDir(value)
        return value
    
    async def setSubRecordDir(self, value):
        """Set the DIR value for all cadRecord instances to match applyRecord's DIR."""
        for sub_record in self.sub_records:
            print(f'{sub_record.prefix} Processing ...')
            
            await sub_record.DIR.write(value)

            # results
            ret_val  = sub_record.VAL.value
            ret_mess = sub_record.MESS.value

            print(f'{sub_record.prefix} CAD VAL: {str(ret_val)}')

            await self.VAL.write(ret_val)
            await self.MESS.write(ret_mess)
            
            if sub_record.VAL.value == 'ERROR':
                print("Error processing cad record: " + sub_record.prefix)
                print("VAL: " + ret_val)
                print("MESS: " + ret_mess)
                break    


    # ------------------ VAL  ------------------------- 
    VAL = pvproperty(
        value=0,  # Assuming 0 as the default integer value
        dtype=caproto.ChannelType.LONG,
        name="VAL"
    )


    @VAL.putter
    async def VAL(self, instance, value):
        await self.VALputter(instance, value)

    async def VALputter(self, instance, value):
        print(f'{self.prefix}VAL value changed to: {value}')


    # ------------------ CLID  ------------------------- 
    CLID = pvproperty(value=0, dtype=caproto.ChannelType.LONG, name="CLID")
    @CLID.putter
    async def CLID(self, instance, value):
        await self.CLIDputter(instance, value)

    async def CLIDputter(self, instance, value):
        print(f'{self.prefix}CLID value changed to: {value}')

    # ------------------ MESS  ------------------------- 
    MESS = pvproperty(value='N/A', dtype=caproto.ChannelType.STRING, name="MESS")
    @MESS.putter
    async def MESS(self, instance, value):
        await self.MESSputter(instance, value)

    async def MESSputter(self, instance, value):
        print(f'{self.prefix}MESS value changed to: {value}')












